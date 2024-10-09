from django.db import models
from datetime import datetime
from Offers.models import Coupon
from django.core.exceptions import ValidationError
from Turf.models import *
from  django.db.models import Sum
from User.models import UserModel
from django.db.models.signals import post_save
from Offers.models import Coupon
# Assuming TimeSlot and other related models are defined appropriately

class BaseSlot(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    field = models.ForeignKey(SportField, on_delete=models.CASCADE, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        abstract = True  # Abstract base class

    def clean(self):
        super().clean()
        if self.end_time <= self.start_time:
            if not (self.start_time.hour == 23 and self.end_time == datetime.strptime("00:00", "%H:%M").time()):
                raise ValidationError("End time must be after start time.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def calculate_duration(self):
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)
        duration = (end_datetime - start_datetime).total_seconds() / 3600  
        return duration

    def get_price(self):
        # Calculate duration
        duration = self.calculate_duration()
        
        # Find overlapping time slots
        overlapping_time_slots = TimeSlot.objects.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        slot_ids = [slot.id for slot in overlapping_time_slots]

        if not slot_ids:
            raise ValidationError("No overlapping time slot found for the selected start and end times.")

        print("Overlapping Time slot IDs: ", slot_ids)
        print("Duration: ", duration)
        print("Field ID: ", self.field.id)
        print("Turf ID:", self.turf.id)

        total_price = 0

        if slot_ids[0]:
            print("Slot ID is valid: ", slot_ids[0])
            
            price_entries = Price.objects.filter(
            turf=self.turf, 
            field=self.field,
            time_slot_id=slot_ids[0], 
            duration_hours=duration
            )
            price_entry = price_entries.first()
            
            if price_entry:
                total_price = price_entry.price_per_hour
                print("Price: ", total_price)
            else:
                raise ValidationError(f"Price not defined for time slot {slot_ids[0]} and duration {duration} hours.")
        else:
            raise ValidationError("No available time slots found.")

        if total_price == 0:
            raise ValidationError("No applicable price found for the selected duration and time slot.")

        return total_price
    
    def calculate_price(self):
        total_price = self.get_price()

        # Apply coupon discount if available
        if self.coupon:
            if hasattr(self.coupon, 'discount_percentage') and self.coupon.discount_percentage:
                total_price -= total_price * (self.coupon.discount_percentage / 100)
            elif hasattr(self.coupon, 'discount_amount') and self.coupon.discount_amount:
                total_price -= self.coupon.discount_amount

        return total_price

    def __str__(self):
        return f"{self.turf.name} ({self.field.field_type}) - {self.date} {self.start_time} to {self.end_time}"

class TurfSlot(BaseSlot):
    sports = models.CharField(max_length=256, choices=[('Cricket', 'Cricket'), ('Football', 'Football')], null=True, blank=True)

    class Meta:
        unique_together = ('turf', 'date', 'start_time', 'end_time','field')


class BadmintonSlot(BaseSlot):
    pass


class SwimmingSession(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    price_per_person = models.DecimalField(max_digits=6, decimal_places=2, default=200.00)

    def __str__(self):
        return f"Session from {self.start_time} to {self.end_time}"

    class Meta:
        unique_together = ('start_time', 'end_time')
        ordering = ['start_time']

    def clean(self):
        super().clean()
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def remaining_capacity(self, date):
        total_people = SwimmingSlot.objects.filter(session=self, date=date).aggregate(Sum('number_of_people'))['number_of_people__sum'] or 0
        return self.capacity - total_people

class SwimmingSlot(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    field = models.ForeignKey(SportField, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(SwimmingSession, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    number_of_people = models.PositiveIntegerField()
    is_booked = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('session', 'date', 'field')

    def available_capacity(self):
        return self.session.remaining_capacity(self.date)

    def book_slot(self, number_of_people):
        if number_of_people <= 0:
            raise ValueError("Number of people must be greater than zero.")
        if self.available_capacity() < number_of_people:
            raise ValueError("Not enough capacity to book the slot.")
        self.number_of_people += number_of_people
        self.save()

    def total_price(self):
        return self.number_of_people * self.session.price_per_person

    def calculate_price(self):
        total_price = self.total_price()

        if self.coupon:
            if hasattr(self.coupon, 'discount_percentage') and self.coupon.discount_percentage:
                total_price -= total_price * (self.coupon.discount_percentage / 100)
            elif hasattr(self.coupon, 'discount_amount') and self.coupon.discount_amount:
                total_price -= self.coupon.discount_amount

        return total_price
    
from datetime import time, timedelta

def create_hourly_sessions():
 
    start_of_day = time(6, 0)
    end_of_day = time(21, 0)
    current_time = start_of_day

    while current_time < end_of_day:
        end_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
        session = SwimmingSession.objects.create(
            start_time=current_time,
            end_time=end_time,
            capacity=20, 
            price_per_person=200.00  
        )
        session.save()
        current_time = end_time

class SlotHistory(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    turf_slot = models.ForeignKey(TurfSlot, null=True, blank=True, on_delete=models.CASCADE)
    badminton_slot = models.ForeignKey(BadmintonSlot, null=True, blank=True, on_delete=models.CASCADE)
    swimming_slot = models.ForeignKey(SwimmingSlot, null=True, blank=True, on_delete=models.CASCADE)
    booking_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Slot booked by {self.user.username} on {self.booking_date}"