# Generated by Django 5.0.6 on 2024-10-09 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='max_otp_try',
            field=models.IntegerField(default=3),
        ),
    ]