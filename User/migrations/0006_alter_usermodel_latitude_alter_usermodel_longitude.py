# Generated by Django 5.0.6 on 2024-10-19 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0005_usermodel_latitude_usermodel_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
    ]
