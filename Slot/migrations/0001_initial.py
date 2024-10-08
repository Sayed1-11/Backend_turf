# Generated by Django 5.0.6 on 2024-10-03 15:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Offers', '0001_initial'),
        ('Turf', '0003_remove_sloteligibility_field_sloteligibility_turf'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BadmintonSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('date', models.DateField()),
                ('is_booked', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Offers.coupon')),
                ('field', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Turf.sportfield')),
                ('turf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Turf.turf')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SwimmingSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('capacity', models.PositiveIntegerField(default=20)),
                ('price_per_person', models.DecimalField(decimal_places=2, default=200.0, max_digits=6)),
            ],
            options={
                'ordering': ['start_time'],
                'unique_together': {('start_time', 'end_time')},
            },
        ),
        migrations.CreateModel(
            name='SwimmingSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('date', models.DateField()),
                ('is_booked', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('number_of_people', models.PositiveIntegerField()),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Offers.coupon')),
                ('field', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Turf.sportfield')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Slot.swimmingsession')),
                ('turf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Turf.turf')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TurfSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('date', models.DateField()),
                ('is_booked', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('sports', models.CharField(blank=True, choices=[('Cricket', 'Cricket'), ('Football', 'Football')], max_length=256, null=True)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Offers.coupon')),
                ('field', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Turf.sportfield')),
                ('turf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Turf.turf')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('turf', 'date', 'start_time', 'end_time')},
            },
        ),
    ]
