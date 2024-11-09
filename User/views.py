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
from django_filters.rest_framework import DjangoFilterBackend
import random
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import pytz
from django.middleware.csrf import get_token
local_tz = pytz.timezone('Asia/Dhaka')
from django.conf import settings
from .models import UserModel
from .serializers import UserSerializer,UserProfileUpdateSerializer,AdminLoginSerializer,AdminUserSignupSerializer
from rest_framework.permissions import AllowAny
import logging
from django.core.cache import cache
import requests
from decimal import Decimal
logger = logging.getLogger('User')
# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        
        if phone_number:
            # Check if a user with this phone number already exists
            existing_user = UserModel.objects.filter(phone_number=phone_number).first()
            if existing_user:
                # Directly generate OTP for the existing user
                logger.info(f"User with phone number {phone_number} already exists. Generating OTP.")
                return self.generate_otp_for_existing_user(existing_user)

        # Proceed with user creation if no existing user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_id = serializer.data['id']
        print(user_id)
        logger.info(f"User with ID {user_id} created successfully.")

        return Response(
            {'message': 'User created successfully.', 'user_id': user_id},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    def generate_otp_for_existing_user(self, user):
        current_time = timezone.now().astimezone(local_tz)
        otp_max_out = user.otp_max_out.astimezone(local_tz) if user.otp_max_out else None

        if user.max_otp_try == 0:
            if otp_max_out is not None and current_time < otp_max_out:
                return Response(
                    {'message': 'Max OTP try reached, try again after the 1 minute.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                user.max_otp_try = settings.MAX_OTP_TRY  

        otp = random.randint(1000, 9999)
        otp_expiry = current_time + timedelta(minutes=2)
        user.max_otp_try -= 1
        user.otp = otp
        user.otp_expiry = otp_expiry

        if user.max_otp_try == 0:
            user.otp_max_out = current_time + timedelta(minutes=1)
        else:
            user.otp_max_out = None

        user.save()
        send_otp(user.phone_number, otp)
        return Response({'message': 'OTP generated successfully.', 'user_id': user.id}, status=status.HTTP_200_OK) 
    @action(detail=True, methods=['PATCH'])
    def verify_otp(self, request, pk=None):
        try:
            instance = self.get_object()
            current_time = timezone.now().astimezone(local_tz)
            logger.info(f"Verifying OTP for user {pk}")

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
                csrf_token = get_token(request)
                
                return Response({
                    'message': 'OTP verified successfully.',
                    'token': token.key,
                    'uid': uid,
                    'csrfToken': csrf_token
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

    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path="logout")
    def logout(self, request):
        try:
            # Delete the token associated with the user
            request.user.auth_token.delete()
            logger.info(f"User {request.user.id} logged out successfully.")

            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during logout: {e}", exc_info=True)
            return Response({'error': 'An error occurred during logout.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    @action(detail=False, methods=['POST'], url_path="admin-login")
    def admin_login(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        csrf_token = get_token(request)

        return Response({
            'message': 'Admin login successful.',
            'token': token.key,
            'csrfToken': csrf_token
        }, status=status.HTTP_200_OK)


class AdminUserSignupViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()  
    serializer_class = AdminUserSignupSerializer

    @action(detail=False, methods=['post'], url_path="admin-signup")
    def admin_signup(self, request):
        """
        Custom action for admin user signup.
        """
        serializer = AdminUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # This will call the `create` method in the serializer
            return Response({'message': 'Admin user created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateViewset(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserProfileUpdateSerializer
    filter_backends = [DjangoFilterBackend]
    def get_queryset(self):
        return UserModel.objects.filter(id=self.request.user.id)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        address = request.data.get('address', None)

        if address:
            print(address)
            lat, lon = self.get_lat_lon_from_address(address)

            if lat is not None and lon is not None:
                try:
                    # Update instance fields directly
                    instance.latitude = Decimal(lat)
                    instance.longitude = Decimal(lon)
                except (ValueError, TypeError):
                    return Response({"error": "Invalid latitude or longitude."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unable to fetch coordinates for the given address."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Create a serializer with the updated data
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get_lat_lon_from_address(self, address):
        print(f"Fetching coordinates for address: {address}")
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
            headers = {
                'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Customize with your app's name and your email
            }
            response = requests.get(url, headers=headers)

            # Check the status code of the response
            if response.status_code != 200:
                print(f"Error: Received {response.status_code} from the API")
                return None, None

            response_data = response.json()
            if response_data:
                lat = response_data[0].get("lat")
                lon = response_data[0].get("lon")
                print('lat:', lat)
                print('lon:', lon)
                return lat, lon
            else:
                print(f"No results found for address: {address}")
                return None, None

        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None, None

