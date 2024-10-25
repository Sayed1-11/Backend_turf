from django.db import models
from Offers.models import Coupon
from datetime import datetime,timedelta
from User.models import UserModel
from django.utils.translation import gettext_lazy as _
class Facility(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Sports(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sport', blank=True)
    def __str__(self):
        return self.name




class Turf(models.Model):
    User = models.ForeignKey(UserModel, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True) 
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
            return round(average_rating, 1)  
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
    turf = models.ForeignKey(Turf, related_name='time_slots', on_delete=models.CASCADE,null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, blank=True, null=True)

    def calculate_duration(self):
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)

        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)

        # Calculate the duration in hours
        duration = (end_datetime - start_datetime).total_seconds() / 3600
        return duration

    def save(self, *args, **kwargs):
        self.duration = self.calculate_duration()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} ({self.duration} hours) -{self.turf}"

DAYS_OF_WEEK_CHOICES = [
    ('Mon', _('Monday')),
    ('Tue', _('Tuesday')),
    ('Wed', _('Wednesday')),
    ('Thu', _('Thursday')),
    ('Fri', _('Friday')),
    ('Sat', _('Saturday')),
    ('Sun', _('Sunday')),
]

class Price(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, blank=True, null=True)
    field = models.ForeignKey(SportField, related_name='prices', on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)

    # New field to specify applicable days of the week
    days_of_week = models.CharField(
        max_length=21,  # Maximum length for storing multiple day abbreviations
        choices=DAYS_OF_WEEK_CHOICES,
        default='Mon',
    )

    def __str__(self):
        return f"{self.field.field_type} - {self.time_slot} - {self.price_per_hour} {self.currency} on {self.days_of_week}"


class SlotEligibility(models.Model):
    Turf = models.ForeignKey(Turf, related_name='slot_eligibilities',on_delete=models.CASCADE,null=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, null=True, blank=True)  

    def __str__(self):
        return f"{self.Turf.name} - {self.time_slot} - {'Available' if self.is_available else 'Unavailable: ' + self.reason}"


class Review(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Assuming a 1-5 rating scale
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} on {self.turf.name}'

    class Meta:
        unique_together = ['user', 'turf'] 