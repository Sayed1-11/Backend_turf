# Generated by Django 5.0.6 on 2024-10-05 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Turf', '0004_price_turf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='Turf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Turf.turf'),
        ),
        migrations.AlterField(
            model_name='sloteligibility',
            name='Turf',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slot_eligibilities', to='Turf.turf'),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='duration',
            field=models.DecimalField(blank=True, decimal_places=1, default=1.0, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='turf',
            name='sports',
            field=models.ManyToManyField(to='Turf.sports'),
        ),
    ]
