from rest_framework import serializers
from .models import UserModel
from .utils import send_otp
from django.utils import timezone
import pytz,requests
from datetime import timedelta
local_tz = pytz.timezone('Asia/Dhaka')
import random
from Booking.models import Turf_Booking,Badminton_Booking,Swimming_Booking
from django.conf import settings
import logging
logger = logging.getLogger('User')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id',
            "phone_number", 
        )

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits and numeric.")
   
        return value

    def create(self, validated_data):
        try:
            otp = random.randint(1000, 9999)
            otp_expiry = timezone.now().astimezone(local_tz) + timedelta(minutes=5)
            user = UserModel(
                phone_number=validated_data["phone_number"],
                otp=otp,
                otp_expiry=otp_expiry,
                max_otp_try=settings.MAX_OTP_TRY,
            )
            user.save()
            send_otp(validated_data["phone_number"], otp)
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the user.")

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()
    group_play = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    class Meta:
        model = UserModel
        fields = (
            "id",
            "email",
            'profile_image',
            "name",
            "birthdate",
            "phone_number",
            "gender",
            "address",
            "longitude",
            "latitude",
            "bookings",
            "group_play",  # Add group_play field
            "points"
        )

        read_only_fields = ["longitude",
            "latitude"]
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def get_bookings(self, obj):
        # Initialize booking count
        total_bookings_count = 0
        
        # Count bookings from Swimming_Booking model
        swimming_bookings_count = Swimming_Booking.objects.filter(user=obj).count()
        total_bookings_count += swimming_bookings_count

        # Count bookings from Turf_Booking model
        turf_bookings_count = Turf_Booking.objects.filter(user=obj).count()
        total_bookings_count += turf_bookings_count

        # Count bookings from Badminton_Booking model
        badminton_bookings_count = Badminton_Booking.objects.filter(user=obj).count()
        total_bookings_count += badminton_bookings_count

        return total_bookings_count
    def get_group_play(self, obj):
        return 0  

    def get_points(self, obj):

        return 0

class AdminUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ('phone_number', 'password')

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits and numeric.")
        if UserModel.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        user = UserModel.objects.create(
            phone_number=validated_data['phone_number'],
            role='admin', 
            is_active=True,  
            is_staff=True,  
            is_superuser=False  
        )
        user.set_password(validated_data['password'])  
        user.save()

        return user


class AdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        try:
            user = UserModel.objects.get(phone_number=phone_number, role='admin')
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("User does not exist or is not an admin.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        if not user.is_active:
            raise serializers.ValidationError("Admin account is inactive.")

        data['user'] = user
        return data
