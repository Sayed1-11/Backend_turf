# Generated by Django 5.0.6 on 2024-11-13 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Turf', '0015_remove_turf_duration_alter_timeslot_duration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TurfAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Turf.turf')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                ('turf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='Turf.turf')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'turf')},
            },
        ),
    ]
