from django.db import models
from Slot.models import TurfSlot,BadmintonSlot,SwimmingSlot

class Coupon(models.Model):
    ISSUER_CHOICES = (
        ('APP_OWNER', 'App Owner'),
        ('TURF_OWNER', 'Turf Owner'),
    )
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    issued_by = models.CharField(
        max_length=10,
        choices=ISSUER_CHOICES,
        default='APP_OWNER',  
    )

    
    def __str__(self):
        return self.code


class TurfCouponApply(models.Model):
    offer = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    slot = models.ForeignKey(TurfSlot, on_delete=models.CASCADE)

    def __str__(self):
        return f"Coupon {self.coupon.code} applied to Turf Slot {self.slot}"

class BadmintonCouponApply(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    slot = models.ForeignKey(BadmintonSlot, on_delete=models.CASCADE)

    def __str__(self):
        return f"Coupon {self.coupon.code} applied to Badminton Slot {self.slot}"

class SwimmingCouponApply(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    slot = models.ForeignKey(SwimmingSlot, on_delete=models.CASCADE)

    def __str__(self):
        return f"Coupon {self.coupon.code} applied to Swimming Slot {self.slot}"
