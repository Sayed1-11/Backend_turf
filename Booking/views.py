from rest_framework import viewsets
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking
from .serializers import (
    TurfBookingSerializer,
    BadmintonBookingSerializer,
    SwimmingBookingSerializer,
)

class TurfBookingViewSet(viewsets.ModelViewSet):
    queryset = Turf_Booking.objects.all()
    serializer_class = TurfBookingSerializer

    def perform_create(self, serializer):
        # Create the booking
        booking = serializer.save()

        # Update the corresponding slots
        booking.turf_slot.is_booked = True
        booking.turf_slot.is_available = False
        booking.turf_slot.save()

class BadmintonBookingViewSet(viewsets.ModelViewSet):
    queryset = Badminton_Booking.objects.all()
    serializer_class = BadmintonBookingSerializer

    def perform_create(self, serializer):
        # Create the booking
        booking = serializer.save()

        # Update the corresponding slots
        booking.badminton_slot.is_booked = True
        booking.badminton_slot.is_available = False
        booking.badminton_slot.save()

class SwimmingBookingViewSet(viewsets.ModelViewSet):
    queryset = Swimming_Booking.objects.all()
    serializer_class = SwimmingBookingSerializer

    def perform_create(self, serializer):
        # Create the booking
        booking = serializer.save()

        # Update the corresponding slots
        booking.swimming_slot.is_booked = True
        booking.swimming_slot.is_available = False
        booking.swimming_slot.save()
