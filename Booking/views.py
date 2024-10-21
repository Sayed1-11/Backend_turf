from rest_framework import viewsets,filters
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking
from .serializers import (
    TurfBookingSerializer,
    BadmintonBookingSerializer,
    SwimmingBookingSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status,renderers
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
import requests,usaddress,logging,uuid
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
filter_backends = [DjangoFilterBackend, filters.SearchFilter]
from aamarpay.aamarpay import aamarPay
from django.conf import settings

class TurfBookingViewSet(viewsets.ModelViewSet):
    queryset = Turf_Booking.objects.all()
    serializer_class = TurfBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'turf_slot']

    def get_serializer_context(self):
        return super().get_serializer_context() 
    def create(self, request, *args, **kwargs):
        # Initialize serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Update turf_slot status
        booking.turf_slot.is_booked = True
        booking.turf_slot.is_available = False
        booking.turf_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        booking.save()

        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  # Get mobile from request or use a default

        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl='https://backend-turf.onrender.com/payment/success/',  # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',  # Replace with actual cancel URL
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for turf slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  # Set actual customer mobile
            customerAddress1=request.user.address or '123 Street Name',  # Use user profile or default
            customerAddress2=request.user.address or 'Apt 4B',  # Use user profile or default
            customerCity= 'City Name',  # Use user profile or default
            customerState='State Name',  # Use user profile or default
            customerPostCode='12345'  # Use user profile or default
        )

        # Get payment URL
        payment_url = pay.payment()

        # Handle payment initiation failure
        if not payment_url:
            logging.error("Payment URL not found during payment initiation.")
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(f"Payment URL: {payment_url}")
        return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
        
class BadmintonBookingViewSet(viewsets.ModelViewSet):
    queryset = Badminton_Booking.objects.all()
    serializer_class = BadmintonBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'badminton_slot']
    def get_serializer_context(self):
        return super().get_serializer_context()
    def create(self, request, *args, **kwargs):
        # Initialize serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Update turf_slot status
        booking.badminton_slot.is_booked = True
        booking.badminton_slot.is_available = False
        booking.badminton_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        booking.save()

        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  # Get mobile from request or use a default

        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl='https://backend-turf.onrender.com/payment/success/',  # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',  # Replace with actual cancel URL
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for turf slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  # Set actual customer mobile
            customerAddress1=request.user.address or '123 Street Name',  # Use user profile or default
            customerAddress2=request.user.address or 'Apt 4B',  # Use user profile or default
            customerCity= 'City Name',  # Use user profile or default
            customerState='State Name',  # Use user profile or default
            customerPostCode='12345'  # Use user profile or default
        )

        # Get payment URL
        payment_url = pay.payment()

        # Handle payment initiation failure
        if not payment_url:
            logging.error("Payment URL not found during payment initiation.")
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(f"Payment URL: {payment_url}")
        return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)

class SwimmingBookingViewSet(viewsets.ModelViewSet):
    queryset = Swimming_Booking.objects.all()
    serializer_class = SwimmingBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'swimming_slot']

    def create(self, request, *args, **kwargs):
        # Initialize serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        booking.swimming_slot.is_booked = True
        booking.swimming_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        booking.save()

        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  # Get mobile from request or use a default

        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl='https://backend-turf.onrender.com/payment/success/',  # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for Swimming slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  # Set actual customer mobile
            customerAddress1=request.user.address or '123 Street Name',  # Use user profile or default
            customerAddress2=request.user.address or 'Apt 4B',  # Use user profile or default
            customerCity= 'City Name',  # Use user profile or default
            customerState='State Name',  # Use user profile or default
            customerPostCode='12345'  # Use user profile or default
        )

        # Get payment URL
        payment_url = pay.payment()

        # Handle payment initiation failure
        if not payment_url:
            logging.error("Payment URL not found during payment initiation.")
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(f"Payment URL: {payment_url}")
        return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
@csrf_exempt
def aamarpay_callback(request):
    # Log the callback request data for debugging purposes
    logging.info(f"Callback request data: {request.GET}")
    transaction_id = request.GET.get('mer_txnid')

    # Ensure transaction_id exists
    if not transaction_id:
        logging.error("Missing transaction ID in callback.")
        return HttpResponse("Missing transaction ID", status=status.HTTP_400_BAD_REQUEST)

    # Check each booking type to find the transaction ID
    booking = None
    for booking_model in [Turf_Booking, Badminton_Booking, Swimming_Booking]:
        try:
            booking = booking_model.objects.get(transaction_id=transaction_id)
            break  # If booking is found, break out of the loop
        except booking_model.DoesNotExist:
            continue  # If not found in this model, continue checking other models

    # If no booking is found, return an error response
    if not booking:
        logging.error(f"Booking not found for transaction ID: {transaction_id}")
        return HttpResponse("Invalid transaction ID", status=status.HTTP_400_BAD_REQUEST)

    # Check the payment status and update the booking accordingly
    payment_status = request.GET.get('pay_status')

    if payment_status == 'Successful':
        booking.payment_status = 'successful'
        if booking.total_amount == booking.advance_payable:
            booking.is_paid_full = True
        booking.status = 'confirmed'
        booking.save() 
        logging.info(f"Payment successful for transaction ID: {transaction_id}")
        return redirect('payment_success')  # Ensure this URL is properly defined in your project
    else:
        booking.payment_status = 'failed'
        booking.save()
        logging.warning(f"Payment failed for transaction ID: {transaction_id}")
        return redirect('payment_failure')  # Ensure this URL is properly defined in your project
@csrf_exempt
def payment_success(request):
    return HttpResponse("Payment Successful")

@csrf_exempt
def payment_failure(request):
    return HttpResponse("Payment Failed")
