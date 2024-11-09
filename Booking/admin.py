from django.contrib import admin
from .models import Turf_Booking,Badminton_Booking,Swimming_Booking,Booking_History
# Register your models here.
admin.site.register(Turf_Booking)
admin.site.register(Badminton_Booking)
admin.site.register(Swimming_Booking)
admin.site.register(Booking_History)