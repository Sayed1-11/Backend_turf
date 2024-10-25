from django.db import models
from User.models import UserModel
from Offers.models import Coupon
from Slot.models import TurfSlot, BadmintonSlot, SwimmingSlot,SwimmingSession
from datetime import datetime
from Turf.models import SportField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from celery import shared_task

class BaseBooking(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    order_id = models.CharField(max_length=7, blank=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    is_paid_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], default='ongoing')
    payment_status = models.CharField(max_length=20, choices=[
        ('initiated', 'Initiated'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='pending')
    payment_reference = models.CharField(max_length=50, blank=True, null=True)  # Stores Aamarpay transaction reference
    payment_response = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True  

    


class Turf_Booking(BaseBooking):
    turf_slot = models.ForeignKey(TurfSlot, on_delete=models.CASCADE)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2, default=500.0)
    def save(self, *args, **kwargs):
        self.total_amount = self.turf_slot.calculate_price()
        self.due_amount = self.total_amount - self.advance_payable
        if not self.order_id:
            current_year = datetime.now().year + self.turf_slot.turf.id
            booking_count = Turf_Booking.objects.count() + 1
            self.order_id = f"{self.turf_slot.id}{current_year}{booking_count}"
        super().save(*args, **kwargs)
    
    def update_status_based_on_time(self):
        # Assuming you have start_time and end_time in TurfSlot model
        current_time = timezone.now()
        if current_time >= self.turf_slot.end_time:
            self.status = 'completed'
        else:
            self.status = 'ongoing'
        self.save()
@receiver(post_save, sender=Turf_Booking)
def update_turf_slot_status(sender, instance, **kwargs):
    if instance.payment_status == 'successful' :
        instance.turf_slot.is_booked = True
        instance.turf_slot.is_available = False
    elif instance.payment_status == 'failed':
        instance.turf_slot.is_booked = False
        instance.turf_slot.is_available = True
    instance.turf_slot.save()


class Badminton_Booking(BaseBooking):
    badminton_slot = models.ForeignKey(BadmintonSlot, on_delete=models.CASCADE)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2, default=300.0)
    def save(self, *args, **kwargs):
        self.total_amount = self.badminton_slot.calculate_price()
        self.due_amount = self.total_amount - self.advance_payable
        if not self.order_id:
            current_year = datetime.now().year + self.badminton_slot.turf.id
            booking_count = Badminton_Booking.objects.count() + 1
            self.order_id = f"{self.badminton_slot.id}{current_year}{booking_count}"
        super().save(*args, **kwargs)


@receiver(post_save, sender=Badminton_Booking)
def update_badminton_slot_status(sender, instance, **kwargs):
    if instance.payment_status == 'successful':
        instance.badminton_slot.is_booked = True
        instance.badminton_slot.is_available = False
    elif instance.payment_status == 'failed':
        instance.badminton_slot.is_booked = False
        instance.badminton_slot.is_available = True
    instance.badminton_slot.save()


class Swimming_Booking(BaseBooking):
    swimming_slot = models.ForeignKey(SwimmingSlot, on_delete=models.CASCADE)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2, default=300.0)
    def save(self, *args, **kwargs):
        self.total_amount = self.swimming_slot.calculate_price()
        if not self.order_id:
            current_year = datetime.now().year + self.swimming_slot.turf.id
            booking_count = Swimming_Booking.objects.count() + 1
            self.order_id = f"{self.swimming_slot.id}{current_year}{booking_count}"
        super().save(*args, **kwargs)


@receiver(post_save, sender=Swimming_Booking)
def update_swimming_slot_status(sender, instance, **kwargs):
    if instance.payment_status == 'successful':
        instance.swimming_slot.is_booked = True
    elif instance.payment_status == 'failed':
        instance.swimming_slot.is_booked = False
    instance.swimming_slot.save()

class Booking_History(models.Model):
    turf_book = models.ForeignKey(Turf_Booking, null=True, blank=True, on_delete=models.CASCADE)
    badminton_book = models.ForeignKey(Badminton_Booking, null=True, blank=True, on_delete=models.CASCADE)
    swimming_book = models.ForeignKey(Swimming_Booking, null=True, blank=True, on_delete=models.CASCADE)
    booking_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return f"Slot booked by {self.user.username} on {self.booking_date}"