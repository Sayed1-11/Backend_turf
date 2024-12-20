from django.db import models
from User.models import UserModel
from Offers.models import Coupon
from Slot.models import TurfSlot, BadmintonSlot, SwimmingSlot
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from celery import shared_task
from decimal import Decimal

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
        discount = Decimal(0) 
        if self.coupon:
            if not self.coupon.is_active:
                raise ValueError("The selected coupon is inactive.")
            discount = self.coupon.discount_amount
            self.discount = discount
            self.total_amount = max(Decimal(0), self.total_amount - discount)
        if self.advance_payable > self.total_amount:
            raise ValueError("Advance payment cannot exceed the total amount.")
        self.due_amount = self.total_amount - self.advance_payable
        if not self.order_id:
            current_year = datetime.now().year
            booking_count = Turf_Booking.objects.count() + 1
            self.order_id = f"{self.turf_slot.id}{current_year}{booking_count}"

        # Call the parent save method
        super().save(*args, **kwargs)
    @classmethod
    def update_status_for_all(cls):
        current_time = timezone.now()
        bookings = cls.objects.all()

        for booking in bookings:
            booking_end_datetime_naive = datetime.combine(booking.turf_slot.date, booking.turf_slot.end_time)
            booking_end_datetime = timezone.make_aware(booking_end_datetime_naive, timezone.get_current_timezone())
            if current_time >= booking_end_datetime:
                booking.status = 'completed'
            else:
                booking.status = 'ongoing'
            booking.save()



class Badminton_Booking(BaseBooking):
    badminton_slot = models.ForeignKey(BadmintonSlot, on_delete=models.CASCADE)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2, default=300.0)
    def save(self, *args, **kwargs):
        self.total_amount = self.badminton_slot.calculate_price()
        discount = Decimal(0) 
        if self.coupon:
            if not self.coupon.is_active:
                raise ValueError("The selected coupon is inactive.")
            discount = self.coupon.discount_amount
            self.discount = discount
            self.total_amount = max(Decimal(0), self.total_amount - discount)
        if self.advance_payable > self.total_amount:
            raise ValueError("Advance payment cannot exceed the total amount.")
        self.due_amount = self.total_amount - self.advance_payable
        if not self.order_id:
            current_year = datetime.now().year + self.badminton_slot.turf.id
            booking_count = Badminton_Booking.objects.count() + 1
            self.order_id = f"{self.badminton_slot.id}{current_year}{booking_count}"
        super().save(*args, **kwargs)

    @classmethod
    def update_status_for_all(cls):
        current_time = timezone.now()

        bookings = cls.objects.all()

        for booking in bookings:
            booking_end_datetime_naive = datetime.combine(booking.badminton_slot.date, booking.badminton_slot.end_time)
            booking_end_datetime = timezone.make_aware(booking_end_datetime_naive, timezone.get_current_timezone())
            if current_time >= booking_end_datetime:
                booking.status = 'completed'
            else:
                booking.status = 'ongoing'
            booking.save()





class Swimming_Booking(BaseBooking):
    swimming_slot = models.ForeignKey(SwimmingSlot, on_delete=models.CASCADE)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2, default=300.0)
    def save(self, *args, **kwargs):
        self.total_amount = self.swimming_slot.calculate_price()
        discount = Decimal(0) 
        if self.coupon:
            if not self.coupon.is_active:
                raise ValueError("The selected coupon is inactive.")
            discount = self.coupon.discount_amount
            self.discount = discount
            self.total_amount = max(Decimal(0), self.total_amount - discount)
        if self.advance_payable > self.total_amount:
            raise ValueError("Advance payment cannot exceed the total amount.")
        self.due_amount = self.total_amount - self.advance_payable
        if not self.order_id:
            current_year = datetime.now().year + self.swimming_slot.turf.id
            booking_count = Swimming_Booking.objects.count() + 1
            self.order_id = f"{self.swimming_slot.id}{current_year}{booking_count}"
        super().save(*args, **kwargs)
    @classmethod
    def update_status_for_all(cls):
        current_time = timezone.now()

        bookings = cls.objects.all()

        for booking in bookings:
            print(booking)
            # Combine date and time to create a naive datetime
            booking_end_datetime_naive = datetime.combine(booking.swimming_slot.date, booking.swimming_slot.session.end_time)
            booking_end_datetime = timezone.make_aware(booking_end_datetime_naive, timezone.get_current_timezone())

            # Now compare current_time (datetime) with booking_end_datetime (also datetime)
            if current_time >= booking_end_datetime:
                booking.status = 'completed'
            else:
                booking.status = 'ongoing'
            booking.save()



class Booking_History(models.Model):
    turf_book = models.ForeignKey(Turf_Booking, null=True, blank=True, on_delete=models.CASCADE)
    badminton_book = models.ForeignKey(Badminton_Booking, null=True, blank=True, on_delete=models.CASCADE)
    swimming_book = models.ForeignKey(Swimming_Booking, null=True, blank=True, on_delete=models.CASCADE)
    booking_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payable = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return f"Slot booked by {self.user.username} on {self.booking_date}"

