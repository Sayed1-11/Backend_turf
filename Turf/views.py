from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from .models import Turf, Sports, TimeSlot, Price,SportField,Facility,SlotEligibility,Review,Favorite
from Booking.models import Turf_Booking,Badminton_Booking,Swimming_Booking
from .serializers import TurfSerializer, SportsSerializer, TimeSlotSerializer, PriceSerializer,SportFieldSerializer,FacilitySerializer,SlotEligibilitySerializer,ReviewSerializer,FavoriteSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import math,requests
from django.db.models import Q,F, FloatField
from django.db.models.functions import Cast
from math import radians, cos, sin, acos
from decimal import Decimal


class TurfViewSet(viewsets.ModelViewSet):
    queryset = Turf.objects.all()
    serializer_class = TurfSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sports','location','name']
    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters
        name = self.request.query_params.get('name', None)
        location = self.request.query_params.get('location', None)
        sports = self.request.query_params.getlist('sports', None)

        # Filter by name
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by location
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by multiple sports
        if sports:
            # The 'sports' field should be a many-to-many relation
            queryset = queryset.filter(sports__id__in=sports).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        user = request.user
        user_latitude = user.latitude  
        user_longitude = user.longitude  
        queryset = self.get_queryset()
        
        if user_latitude is not None and user_longitude is not None:
            # Annotate the queryset with distance to the user
            queryset = queryset.annotate(
                distance=self.calculate_distance(user_latitude, user_longitude)
            ).order_by('distance')

        Turf_Booking.update_status_for_all()
        Badminton_Booking.update_status_for_all()
        Swimming_Booking.update_status_for_all()
        

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    def perform_create(self, serializer):
        location = self.request.data.get('location')
        lat, lon = self.get_lat_lon_from_address(location)
        if lat is not None and lon is not None:
            # Prepare the validated data with coordinates
            validated_data = serializer.validated_data.copy()
            validated_data['latitude'] = Decimal(lat)
            validated_data['longitude'] = Decimal(lon)
            print(lat,lon)
            validated_data['User'] = self.request.user
            
            # Create the turf instance
            turf = serializer.save(**validated_data)
            facilities_data = self.request.data.get('facilities', [])
            sports_data = self.request.data.get('sports', [])

            if facilities_data:
                turf.facilities.set(facilities_data)
            if sports_data:
                turf.sports.set(sports_data)
            return Response({'message': 'Turf created successfully.'}, status=status.HTTP_201_CREATED)

        return Response({"error": "Unable to fetch coordinates for the given address."}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            turf = self.get_object()
            serializer = self.get_serializer(turf, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error
            print(f"Error occurred: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_lat_lon_from_address(self, address):
        print(f"Fetching coordinates for address: {address}")
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
            headers = {
                'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Customize with your app's name and your email
            }
            response = requests.get(url, headers=headers)

            # Check the status code of the response
            if response.status_code != 200:
                return None, None

            response_data = response.json()
            if response_data:
                lat = response_data[0].get("lat")
                lon = response_data[0].get("lon")
                return lat, lon
            else:
                print(f"No results found for address: {address}")
                return None, None

        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None, None
    def calculate_distance(self, user_latitude, user_longitude):
        return Cast(
            (
                6371 * math.acos(
                    math.cos(math.radians(user_latitude)) *
                    math.cos(math.radians(F('latitude'))) *
                    math.cos(math.radians(F('longitude')) - math.radians(user_longitude)) +
                    math.sin(math.radians(user_latitude)) *
                    math.sin(math.radians(F('latitude')))
                )
            ), FloatField()
        )
class SportsViewSet(viewsets.ModelViewSet):
    queryset = Sports.objects.all()
    serializer_class = SportsSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    
class FacilitiesViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    
class SportFieldViewSet(viewsets.ModelViewSet):
    queryset = SportField.objects.all()
    serializer_class = SportFieldSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['turf']
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['turf']

    




class TimeSlotEligibilityViewSet(viewsets.ModelViewSet):
    queryset = SlotEligibility.objects.all()
    serializer_class = SlotEligibilitySerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['Turf']

class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['turf']
    
class FieldTypeChoicesView(APIView):
    permission_classes = [IsAuthenticated | IsAdminUser]
    def get(self, request):
        choices = SportField.FIELD_TYPE_CHOICES
        return Response({'field_types': choices})
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'turf'] 
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list' and self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        turf = serializer.validated_data['turf']
        if Review.objects.filter(user=user, turf=turf).exists():
            raise ValidationError("You have already reviewed this turf. You can update your existing review instead.")
        review = serializer.save(user=user)
        review.turf.update_rating()

    def perform_update(self, serializer):
        review = serializer.save()
        review.turf.update_rating()

    def perform_destroy(self, instance):
        turf = instance.turf
        super().perform_destroy(instance)
        turf.update_rating()

class ReviewViewSet_perosn(viewsets.ViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        reviews = Review.objects.filter(user=user)
        review_serializer = ReviewSerializer(reviews, many=True)

        return Response({
            'reviews': review_serializer.data
        })


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    filterset_fields = ['user', 'turf']
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access the endpoints
    
    def perform_create(self, serializer):
        user = self.request.user
        turf = serializer.validated_data.get('turf')

        # Check if this favorite already exists
        if Favorite.objects.filter(user=user, turf=turf).exists():
            raise PermissionDenied("This turf is already in your favorites.")

        # Save the new favorite
        serializer.save(user=user)
    
    def get_queryset(self):
        # Filter the favorites by the logged-in user, so they can only see their own favorites
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Ensure that a user can only delete their own favorites
        if instance.user == self.request.user:
            instance.delete()  # This will delete the favorite
        else:
            raise PermissionDenied("You can only delete your own favorites.")
