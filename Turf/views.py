from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Turf, Sports, TimeSlot, Price,SportField,Facility,SlotEligibility
from .serializers import TurfSerializer, SportsSerializer, TimeSlotSerializer, PriceSerializer,SportFieldSerializer,FacilitySerializer,SlotEligibilitySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.middleware.csrf import get_token
from django_filters.rest_framework import DjangoFilterBackend
import math
from django.db.models import Q,F, FloatField
from django.db.models.functions import Cast

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

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        serializer.save(User=self.request.user)
    

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
    filterset_fields = ['turf']

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