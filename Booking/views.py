from rest_framework import viewsets,filters
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking
from .serializers import (
    TurfBookingSerializer,
    BadmintonBookingSerializer,
    SwimmingBookingSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
filter_backends = [DjangoFilterBackend, filters.SearchFilter]

class TurfBookingViewSet(viewsets.ModelViewSet):
    queryset = Turf_Booking.objects.all()
    serializer_class = TurfBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status','user','turf_slot','id']
    def perform_create(self, serializer):
        booking = serializer.save()
        booking.turf_slot.is_booked = True
        booking.turf_slot.is_available = False
        booking.turf_slot.save()
    
    def get_queryset(self):
        """
        Optionally filter by status query parameter.
        """
        queryset = self.queryset.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset


class BadmintonBookingViewSet(viewsets.ModelViewSet):
    queryset = Badminton_Booking.objects.all()
    serializer_class = BadmintonBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status','user','badminton_slot','id']
    def perform_create(self, serializer):
        booking = serializer.save()
        booking.badminton_slot.is_booked = True
        booking.badminton_slot.is_available = False
        booking.badminton_slot.save()
    
    def get_queryset(self):
        """
        Optionally filter by status query parameter.
        """
        queryset = self.queryset.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

class SwimmingBookingViewSet(viewsets.ModelViewSet):
    queryset = Swimming_Booking.objects.all()
    serializer_class = SwimmingBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status','user','swimming_slot','id']
    def perform_create(self, serializer):
        booking = serializer.save()
        booking.swimming_slot.is_booked = True
        booking.swimming_slot.save()

    def get_queryset(self):
        """
        Optionally filter by status query parameter.
        """
        queryset = self.queryset.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset
