# Generated by Django 5.0.6 on 2024-11-14 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_applied', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Badminton_Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('order_id', models.CharField(blank=True, max_length=7)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('is_paid_full', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='ongoing', max_length=20)),
                ('payment_status', models.CharField(choices=[('initiated', 'Initiated'), ('successful', 'Successful'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('payment_reference', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_response', models.TextField(blank=True, null=True)),
                ('advance_payable', models.DecimalField(decimal_places=2, default=300.0, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Booking_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('advance_payable', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Swimming_Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('order_id', models.CharField(blank=True, max_length=7)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('is_paid_full', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='ongoing', max_length=20)),
                ('payment_status', models.CharField(choices=[('initiated', 'Initiated'), ('successful', 'Successful'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('payment_reference', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_response', models.TextField(blank=True, null=True)),
                ('advance_payable', models.DecimalField(decimal_places=2, default=300.0, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Turf_Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('order_id', models.CharField(blank=True, max_length=7)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('is_paid_full', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='ongoing', max_length=20)),
                ('payment_status', models.CharField(choices=[('initiated', 'Initiated'), ('successful', 'Successful'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('payment_reference', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_response', models.TextField(blank=True, null=True)),
                ('advance_payable', models.DecimalField(decimal_places=2, default=500.0, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
