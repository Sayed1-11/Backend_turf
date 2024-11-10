from celery import shared_task
from django.utils import timezone
from .models import Turf_Booking

@shared_task
def update_booking_status():
    # Your task implementation
    pass
