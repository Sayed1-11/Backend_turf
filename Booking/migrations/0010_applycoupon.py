# Generated by Django 5.0.6 on 2024-11-14 05:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Booking', '0009_booking_history_advance_payable'),
        ('Offers', '0002_coupon_issued_by'),
        ('Slot', '0010_remove_swimmingslot_coupon'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_applied', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Offers.coupon')),
                ('turf_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applied_coupons', to='Slot.turfslot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]