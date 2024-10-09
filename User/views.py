from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import send_otp
from rest_framework.authtoken.models import Token
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
import random
from django.utils import timezone
import pytz
local_tz = pytz.timezone('Asia/Dhaka')
from django.conf import settings
from .models import UserModel
from .serializers import UserSerializer,UserProfileUpdateSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': 'User created successfully.', 'user_id': serializer.data['id']}, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

    @action(detail=True, methods=['PATCH'])
    def verify_otp(self, request, pk=None):
        instance = self.get_object()

        # Convert current time and instance.otp_max_out to the desired timezone
        current_time = timezone.now().astimezone(local_tz)
        otp_max_out = instance.otp_max_out.astimezone(local_tz) if instance.otp_max_out else None
        otp_expiry = instance.otp_expiry.astimezone(local_tz) if instance.otp_expiry else None

        # Check if max_otp_try is 0 and if the lockout period is still active
        if instance.max_otp_try == 0 and current_time < otp_max_out:
            return Response(
                {'message': 'Max OTP attempts reached. Try again after the lockout period.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract the provided OTP from the request data
        provided_otp = request.data.get('otp')

        # Check if the provided OTP matches the stored OTP and if it's still valid
        if (not instance.is_active 
            and provided_otp == instance.otp 
            and otp_expiry 
            and current_time < otp_expiry):
            
            # OTP is correct; activate the user and reset OTP-related fields
            instance.is_active = True
            instance.otp_expiry = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.otp_max_out = None
            instance.save()
            
            # Generate a token for the activated user
            token = default_token_generator.make_token(instance)
            uid = urlsafe_base64_encode(force_bytes(instance))
            
            return Response({
                'message': 'OTP verified successfully.',
                'token': token,
                'uid': uid
            }, status=status.HTTP_200_OK)

        # If OTP is incorrect or expired
        if provided_otp != instance.otp:
            # Reduce max_otp_try by 1 if the provided OTP is incorrect
            instance.max_otp_try -= 1

            # If max_otp_try reaches 0, set a lockout period (e.g., 1 hour)
            if instance.max_otp_try <= 0:
                instance.otp_max_out = current_time + timedelta(minutes=1)
                instance.save()
                return Response(
                    {'message': 'Max OTP attempts reached. Try again after the lockout period.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the updated max_otp_try value
            instance.save()
            return Response(
                {'message': f'Incorrect OTP. {instance.max_otp_try} attempts left.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP has expired
        return Response({'message': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'])
    def generate_otp(self, request, pk=None):
        instance = self.get_object()

        # Convert current time and instance.otp_max_out to the desired timezone
        current_time = timezone.now().astimezone(local_tz)
        otp_max_out = instance.otp_max_out.astimezone(local_tz) if instance.otp_max_out else None

        # Check if max_otp_try is 0 and if the lockout period is still active
        if instance.max_otp_try == 0 and current_time < otp_max_out:
            return Response(
                {'message': 'Max OTP try reached, try again after the lockout period.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Generate a new OTP and set the expiry
        otp = random.randint(1000, 9999)
        otp_expiry = current_time + timedelta(minutes=2)
        instance.max_otp_try -= 1
        instance.otp = otp
        instance.otp_expiry = otp_expiry

        # If max_otp_try reaches 0, set the lockout period
        if instance.max_otp_try == 0:
            instance.otp_max_out = current_time + timedelta(minutes=1)
        else:
            instance.otp_max_out = None

        instance.save()
        send_otp(instance.phone_number, otp)
        return Response({'message': 'OTP generated successfully.', 'otp': otp}, status=status.HTTP_200_OK)  


class UserProfileUpdateViewset(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserProfileUpdateSerializer

    @action(detail=True, methods=['PATCH'])
    def update_profile(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.authtoken.models import Token

def create_token_for_user(user):
    token, created = Token.objects.get_or_create(user=user)
    return token.key
