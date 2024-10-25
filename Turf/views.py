from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from .models import Turf, Sports, TimeSlot, Price,SportField,Facility,SlotEligibility,Review
from Booking.models import Turf_Booking,Badminton_Booking,Swimming_Booking
from .serializers import TurfSerializer, SportsSerializer, TimeSlotSerializer, PriceSerializer,SportFieldSerializer,FacilitySerializer,SlotEligibilitySerializer,ReviewSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import math,requests
from django.db.models import Q,F, FloatField
from django.db.models.functions import Cast
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
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        instance = self.get_object()
        location =  request.data.get('location', instance.location)
        if location:
            print(location)
            lat, lon = self.get_lat_lon_from_address(location)

            if lat is not None and lon is not None:
                try:
                    # Update instance fields directly
                    instance.latitude = Decimal(lat)
                    instance.longitude = Decimal(lon)
                except (ValueError, TypeError):
                    return Response({"error": "Invalid latitude or longitude."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unable to fetch coordinates for the given address."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Create a serializer with the updated data
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.save(User=self.request.user)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Turf updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        # Haversine formula to calculate distance
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
    filterset_fields = ['user']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        turf = serializer.validated_data['turf']

        # Check if the user has already reviewed this turf
        if Review.objects.filter(user=user, turf=turf).exists():
            raise ValidationError("You have already reviewed this turf. You can update your existing review instead.")

        # Save the review and update the turf rating
        review = serializer.save(user=user)
        review.turf.update_rating()

    def perform_update(self, serializer):
        review = serializer.save()
        review.turf.update_rating()

    def perform_destroy(self, instance):
        turf = instance.turf  
        super().perform_destroy(instance)  
        turf.update_rating()