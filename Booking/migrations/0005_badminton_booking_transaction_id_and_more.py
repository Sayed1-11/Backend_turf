# Generated by Django 5.0.6 on 2024-10-21 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Booking', '0004_badminton_booking_payment_reference_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='badminton_booking',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='swimming_booking',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='turf_booking',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
