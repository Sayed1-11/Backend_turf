from rest_framework import serializers
from .models import UserModel
from .utils import send_otp
from django.utils import timezone
import pytz
from datetime import timedelta
local_tz = pytz.timezone('Asia/Dhaka')
import random
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id',
            "phone_number", 
        )

   

    def create(self, validated_data):
        otp = random.randint(1000, 9999)
        otp_expiry = timezone.now().astimezone(local_tz) + timedelta(minutes=2)
        user = UserModel(
            phone_number=validated_data["phone_number"],
            otp=otp,
            otp_expiry=otp_expiry,
            max_otp_try=settings.MAX_OTP_TRY,
        )
        user.save()
        send_otp(validated_data["phone_number"], otp)
        return user


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
