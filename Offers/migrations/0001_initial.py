# Generated by Django 5.0.6 on 2024-11-14 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('issued_by', models.CharField(choices=[('APP_OWNER', 'App Owner'), ('TURF_OWNER', 'Turf Owner')], default='APP_OWNER', max_length=10)),
            ],
        ),
    ]
