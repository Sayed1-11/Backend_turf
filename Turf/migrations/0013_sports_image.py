# Generated by Django 5.0.6 on 2024-10-25 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Turf', '0012_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='sports',
            name='image',
            field=models.ImageField(blank=True, upload_to='sport'),
        ),
    ]
