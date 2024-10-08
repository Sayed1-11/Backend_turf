from django.db import models
from Offers.models import Coupon
from datetime import datetime,timedelta

class Facility(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Sports(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class Turf(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='turf_images/')
    facilities = models.ManyToManyField(Facility)
    rating = models.FloatField(default=0.0)  
    available_offers = models.ManyToManyField(Coupon, blank=True)
    sports = models.ManyToManyField(Sports)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    def __str__(self):
        return self.name

    def calculate_average_rating(self):
        ratings = self.ratings.all()  
        if ratings.exists():
            average_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            return round(average_rating, 1)  # Round to 1 decimal place
        return 0.0

    def update_rating(self):
        self.rating = self.calculate_average_rating()
        self.save()

class SportField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('4A Side', '4A Side'),
        ('6A Side', '6A Side'),
        ('Swimming Adult', 'Swimming Adult'),
    ]
    turf = models.ForeignKey(Turf, related_name='fields', on_delete=models.CASCADE)
    field_type = models.CharField(choices=FIELD_TYPE_CHOICES, max_length=50)
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE)
    width = models.IntegerField()
    height = models.IntegerField()
    def save(self, *args, **kwargs):
        if self.sport not in self.turf.sports.all():
            raise ValueError("Selected sport is not available in the associated turf.")
        super(SportField, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.field_type} - {self.sport.name} - {self.turf}"

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, blank=True, null=True)

    def calculate_duration(self):
        # Convert start_time and end_time to datetime objects using an arbitrary date
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)

        # If the end time is earlier than the start time, it indicates a slot spanning midnight
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)

        # Calculate the duration in hours
        duration = (end_datetime - start_datetime).total_seconds() / 3600
        return duration

    def save(self, *args, **kwargs):
        # Auto-calculate duration before saving the model
        self.duration = self.calculate_duration()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} ({self.duration} hours)"

class Price(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, blank=True, null=True)
    field = models.ForeignKey(SportField, related_name='prices', on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)

    def __str__(self):
        return f"{self.field.field_type} - {self.time_slot} - {self.price_per_hour} {self.currency}"


class SlotEligibility(models.Model):
    Turf = models.ForeignKey(Turf, related_name='slot_eligibilities',on_delete=models.CASCADE,null=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, null=True, blank=True)  # Reason for ineligibility (e.g., "Prayer Break")

    def __str__(self):
        return f"{self.Turf.name} - {self.time_slot} - {'Available' if self.is_available else 'Unavailable: ' + self.reason}"
