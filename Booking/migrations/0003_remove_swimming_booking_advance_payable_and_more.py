# Generated by Django 5.0.6 on 2024-10-08 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Booking', '0002_badminton_booking_swimming_booking_turf_booking_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='swimming_booking',
            name='advance_payable',
        ),
        migrations.AlterField(
            model_name='badminton_booking',
            name='advance_payable',
            field=models.DecimalField(decimal_places=2, default=300.0, max_digits=10),
        ),
    ]
