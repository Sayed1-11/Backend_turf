from django.db import models
from datetime import time, timedelta
from django.core.exceptions import ValidationError
from Turf.models import *
from  django.db.models import Sum
from User.models import UserModel
from django.db.models.signals import post_save
import math
from threading import Timer
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
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    class Meta:
        abstract = True  # Abstract base class

    def clean(self):
        super().clean()
        if self.end_time <= self.start_time:
            if not (self.start_time.hour == 23 and self.end_time == datetime.strptime("00:00", "%H:%M").time()):
                raise ValidationError("End time must be after start time.")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        

    @classmethod
    def schedule_deletion_for_unbooked_slots(cls):
        print(cls)
        def delete_unbooked_slots():
            unbooked_slots = cls.objects.filter(is_booked=False)
            for slot in unbooked_slots:
                    slot.delete()
                    print(f"Slot {slot.id} deleted due to inactivity.")
    
        Timer(120, delete_unbooked_slots).start()
    
    def calculate_duration(self):
        start_datetime = datetime.combine(self.date, self.start_time)
        # Add a day if the booking crosses midnight
        end_datetime = datetime.combine(self.date, self.end_time)
        if self.end_time <= self.start_time:
            end_datetime += timedelta(days=1)
        duration = (end_datetime - start_datetime).total_seconds() / 3600
        return math.ceil(duration)

    def get_price(self):
        duration = self.calculate_duration()
        
        day_of_week = self.date.strftime('%a')

        end_time_adjusted = self.end_time

        # Adjust end time for midnight crossing
        if self.end_time == time(0, 0):
            self.end_time = time(23, 59)
            end_time_adjusted = self.end_time
        elif self.end_time < self.start_time:
            end_datetime = datetime.combine(self.date, self.end_time) + timedelta(days=1)
            end_time_adjusted = end_datetime.time()

        overlapping_time_slots = TimeSlot.objects.filter(
            turf=self.turf,
            start_time__lt=end_time_adjusted,
            end_time__gt=self.start_time
        )
      

        slot_ids = [slot.id for slot in overlapping_time_slots]
   
        
        total_price = 0
        price_count = 0

        
        for slot_id in slot_ids:
            price_entries = Price.objects.filter(
                turf=self.turf,
                field=self.field,
                time_slot_id=slot_id,
                duration_hours=duration,
                days_of_week=day_of_week
            )

            if price_entries.exists():
                price_entry = price_entries.first()
                total_price += price_entry.price_per_hour
                price_count += 1
            else:
                raise ValidationError(f"Price not defined for time slot {slot_id}, duration {duration} hours, and day {day_of_week} for turf {self.turf}.")

        
        if price_count > 0:
            total_price /= price_count
        else:
            raise ValidationError("No applicable price found for the selected duration, time slot, and day of the week.")

        return total_price
    
    def calculate_price(self):
        total_price = self.get_price()

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
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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

        return total_price
    def __str__(self):
        return f"{self.turf.name} ({self.field.field_type}) - {self.date} in {self.session}"
    
    @classmethod
    def schedule_deletion_for_unbooked_slots(cls):
        print(cls)
        def delete_unbooked_slots():
            unbooked_slots = cls.objects.filter(is_booked=False)
            for slot in unbooked_slots:
                    slot.delete()
                    print(f"Slot {slot.id} deleted due to inactivity.")
    
        Timer(120, delete_unbooked_slots).start()


class SlotHistory(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE,null=True )
    turf_slot = models.ForeignKey(TurfSlot, null=True, blank=True, on_delete=models.CASCADE)
    badminton_slot = models.ForeignKey(BadmintonSlot, null=True, blank=True, on_delete=models.CASCADE)
    swimming_slot = models.ForeignKey(SwimmingSlot, null=True, blank=True, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, null=True, blank=True, on_delete=models.CASCADE)  # New turf field
    booking_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def save(self, *args, **kwargs):
        # Determine turf and calculate price based on the associated slot
        if self.turf_slot:
            self.turf = self.turf_slot.turf
            self.user = self.turf_slot.user
            self.total_price = self.turf_slot.calculate_price()
        elif self.badminton_slot:
            self.turf = self.badminton_slot.turf
            self.user = self.badminton_slot.user
            self.total_price = self.badminton_slot.calculate_price()
        elif self.swimming_slot:
            self.turf = self.swimming_slot.turf
            self.user = self.swimming_slot.user
            self.total_price = self.swimming_slot.calculate_price()

        # Call the parent's save method to save the model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Slot booked by {self.user.phone_number} on {self.booking_date}"
