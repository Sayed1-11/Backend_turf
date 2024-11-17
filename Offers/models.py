from django.db import models


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



