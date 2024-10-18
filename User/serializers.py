from rest_framework import serializers
from .models import UserModel
from .utils import send_otp
from django.utils import timezone
import pytz,requests
from datetime import timedelta
local_tz = pytz.timezone('Asia/Dhaka')
import random
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
        )
    def update(self, instance, validated_data):
        # Update the address if it's changed
        address = validated_data.get("address", instance.address)
        
        if address and address != instance.address:
            lat, lon = self.get_lat_lon_from_address(address)
            if lat and lon:
                instance.latitude = lat
                instance.longitude = lon

        # Update other fields as usual
        return super().update(instance, validated_data)

    def get_lat_lon_from_address(self, address):
        try:
            # Use OpenStreetMap's Nominatim API to get coordinates from address
            url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
            response = requests.get(url)
            response_data = response.json()

            if response_data:
                lat = response_data[0].get("lat")
                lon = response_data[0].get("lon")
                return lat, lon

        except Exception as e:
            # Handle errors, optionally log them
            print(f"Error fetching coordinates: {e}")
            return None, None

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
