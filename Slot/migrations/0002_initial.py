# Generated by Django 5.0.6 on 2024-11-14 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Slot', '0001_initial'),
        ('Turf', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='badmintonslot',
            name='field',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Turf.sportfield'),
        ),
        migrations.AddField(
            model_name='badmintonslot',
            name='turf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Turf.turf'),
        ),
    ]
