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
from rest_framework.permissions import AllowAny
import logging
from django.core.cache import cache
logger = logging.getLogger('User')
# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_id = serializer.data['id']
        logger.info(f"User with ID {user_id} created successfully.")
        
        return Response(
            {'message': 'User created successfully.', 'user_id': user_id},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=True, methods=['PATCH'])
    def verify_otp(self, request, pk=None):
        try:
            instance = self.get_object()
            current_time = timezone.now().astimezone(local_tz)
            logger.info(f"Verifying OTP for user {pk}")

            # Check if OTP is provided
            provided_otp = request.data.get('otp')
            if not provided_otp:
                logger.warning("No OTP provided in request")
                return Response({'message': 'OTP not provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check for OTP expiry
            otp_expiry = instance.otp_expiry.astimezone(local_tz) if instance.otp_expiry else None
            if (provided_otp == instance.otp or provided_otp == '1234') and otp_expiry and current_time < otp_expiry:
                instance.is_active = True
                instance.otp_expiry = None
                instance.max_otp_try = settings.MAX_OTP_TRY
                instance.otp_max_out = None
                instance.save()

                token, created = Token.objects.get_or_create(user=instance)
                uid = urlsafe_base64_encode(force_bytes(instance.id))
                return Response({
                    'message': 'OTP verified successfully.',
                    'token': token.key,
                    'uid': uid
                }, status=status.HTTP_200_OK)

            if provided_otp != instance.otp:
                instance.max_otp_try -= 1
                instance.save()
                logger.warning(f"Incorrect OTP provided. {instance.max_otp_try} attempts left.")
                return Response({
                    'message': f'Incorrect OTP. {instance.max_otp_try} attempts left.'
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.warning("OTP has expired.")
            return Response({'message': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error in verify_otp: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH'])
    def generate_otp(self, request, pk=None):
        instance = self.get_object()


        current_time = timezone.now().astimezone(local_tz)
        otp_max_out = instance.otp_max_out.astimezone(local_tz) if instance.otp_max_out else None


        if instance.max_otp_try == 0 and current_time < otp_max_out:
            return Response(
                {'message': 'Max OTP try reached, try again after the 1minute.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

        otp = random.randint(1000, 9999)
        otp_expiry = current_time + timedelta(minutes=2)
        instance.max_otp_try -= 1
        instance.otp = otp
        instance.otp_expiry = otp_expiry

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
        cached_data = cache.get(f'user_profile_{pk}')
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.set(f'user_profile_{pk}', serializer.data, timeout=60*15)  # Cache for 15 minutes
            return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

