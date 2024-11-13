# Generated by Django 5.0.6 on 2024-11-13 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='issued_by',
            field=models.CharField(choices=[('APP_OWNER', 'App Owner'), ('TURF_OWNER', 'Turf Owner')], default='APP_OWNER', max_length=10),
        ),
    ]
