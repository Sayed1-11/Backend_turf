# Generated by Django 5.0.6 on 2024-10-05 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Slot', '0001_initial'),
        ('Turf', '0005_alter_price_turf_alter_sloteligibility_turf_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='turfslot',
            unique_together={('turf', 'date', 'start_time', 'end_time', 'field')},
        ),
    ]