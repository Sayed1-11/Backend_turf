from rest_framework import viewsets,filters
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking,Booking_History
from .serializers import (
    TurfBookingSerializer,
    BadmintonBookingSerializer,
    SwimmingBookingSerializer,
    Booking_HistorySerializer,
)
from Offers.models import Coupon
from Slot.models import TurfSlot,BadmintonSlot,SwimmingSlot
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
from rest_framework.decorators import action


class TurfBookingViewSet(viewsets.ModelViewSet):
    queryset = Turf_Booking.objects.all()
    serializer_class = TurfBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'turf_slot']
    
    def retrieve(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.update_status_for_all()
        serializer = self.get_serializer(booking, context={'request': request})
        print(serializer.data)
        return Response(serializer.data)
    
    
    def create(self, request, *args, **kwargs):
        # Initialize serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        turf_slot_id = request.data.get('turf_slot_id')
        turf_slot = TurfSlot.objects.get(id=turf_slot_id)
        serializer.validated_data['turf_slot_id'] = turf_slot
        booking = serializer.save(user=request.user)
        booking.turf_slot.is_booked = True
        booking.turf_slot.is_available = False
        Booking_History.objects.create(
                turf_book=booking,
                booking_date=booking.turf_slot.date,
                total_price=booking.total_amount,
                advance_payable=booking.advance_payable,
            )
        booking.turf_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        booking.save()
        request.session['booking_id'] = booking.id
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number 
        booking_id = request.session.get('booking_id') # Get mobile from request or use a default
        print('booking_id',booking_id)
        success_url = f'https://backend-turf.onrender.com/payment/success/{booking_id}/'

        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl=success_url,  # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',  # Replace with actual cancel URL
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for turf slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  
            customerAddress1=request.user.address or '123 Street Name',  # Use user profile or default
            customerAddress2=request.user.address or 'Apt 4B',  # Use user profile or default
            customerCity= 'City Name',  # Use user profile or default
            customerState='State Name',  # Use user profile or default
            customerPostCode='12345'  # Use user profile or default
        )
        payment_url = pay.payment()
        if not payment_url:
            booking.delete()  
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'payment_url': payment_url,'transaction id':transaction_id}, status=status.HTTP_200_OK)

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
        turf_slot_id = request.data.get('badminton_slot_id')
        badminton_slot = BadmintonSlot.objects.get(id=turf_slot_id)
        serializer.validated_data['badminton_slot_id'] = badminton_slot
        booking = serializer.save(user=request.user)
        

        # Update turf_slot status
        booking.badminton_slot.is_booked = True
        booking.badminton_slot.is_available = False
        Booking_History.objects.create(
                badminton_book=booking,
                booking_date=booking.badminton_slot.date,
                total_price=booking.total_amount,
                advance_payable=booking.advance_payable,
            )
        booking.badminton_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        booking.save()
        request.session['booking_id'] = booking.id
        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  
        booking_id = request.session.get('booking_id') # Get mobile from request or use a default
        print('booking_id',booking_id)
        success_url = f'https://backend-turf.onrender.com/payment/success/{booking_id}/'
        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl=success_url,   # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',  # Replace with actual cancel URL
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for turf slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  
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
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'payment_url': payment_url,'transaction id':transaction_id}, status=status.HTTP_200_OK)

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

        swimming_slot_id = request.data.get('swimming_slot_id')
        swimming_slot = SwimmingSlot.objects.get(id=swimming_slot_id)
        serializer.validated_data['swimming_slot_id'] = swimming_slot
        booking = serializer.save(user=request.user)

        booking.swimming_slot.is_booked = True
        booking.swimming_slot.save()

        transaction_id = str(uuid.uuid4())
        booking.transaction_id = transaction_id
        Booking_History.objects.create(
                swimming_book=booking,
                booking_date=booking.swimming_slot.date,
                total_price=booking.total_amount,
                advance_payable=booking.advance_payable,
            )
        booking.save()
        request.session['booking_id'] = booking.id
        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  # Get mobile from request or use a default
        booking_id = request.session.get('booking_id') # Get mobile from request or use a default
        success_url = f'https://backend-turf.onrender.com/payment/success/{booking_id}/'
        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl=success_url,   # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',
            transactionID=transaction_id,  # Unique transaction ID
            transactionAmount=str(booking.advance_payable),  # Convert to string if required
            signature=settings.AAMARPAY_SIGNATURE_KEY,  # Your actual signature
            description='Booking for Swimming slot',  # Transaction description
            customerName=customer_name,  # Set actual customer name
            customerEmail=customer_email,  # Set actual customer email
            customerMobile=customer_mobile,  
            customerAddress1=request.user.address or '123 Street Name',  
            customerAddress2=request.user.address or 'Apt 4B', 
            customerCity= 'City Name',  
            customerState='State Name', 
            customerPostCode='12345' 
        )

        # Get payment URL
        payment_url = pay.payment()

        # Handle payment initiation failure
        if not payment_url:
            logging.error("Payment URL not found during payment initiation.")
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(f"Payment URL: {payment_url}")
        return Response({'payment_url': payment_url,'transaction id':transaction_id}, status=status.HTTP_200_OK)


      
@csrf_exempt
def payment_success(request, booking_id):
    print(f"Booking ID from URL: {booking_id}")
    if not booking_id:
            return HttpResponse("Booking ID is required", status=400)  
    booking = None
    for model, model_name in [(Turf_Booking, 'turf'), (Badminton_Booking, 'badminton'), (Swimming_Booking, 'swimming')]:
        try:
            booking = model.objects.get(id=booking_id)
            break
        except model.DoesNotExist:
            continue

    if not booking:
        return HttpResponse("Booking not found", status=400)

    transaction_id = booking.transaction_id
    payment_status = 'Successful'

    try:
        return aamarpay_callback(request, transaction_id, payment_status)
         
    except Exception as e:
        logging.error(f"Error in calling Aamarpay callback: {str(e)}")
        return HttpResponse("Error during callback processing", status=500)

    # Optionally, clean up session data after the callback
    
@csrf_exempt
def aamarpay_callback(request, transaction_id, payment_status):
    
    if not transaction_id:
        return HttpResponse("Missing transaction ID", status=status.HTTP_400_BAD_REQUEST)

    # Look up the booking based on the transaction ID
    booking = None
    for booking_model in [Turf_Booking, Badminton_Booking, Swimming_Booking]:
        try:
            booking = booking_model.objects.get(transaction_id=transaction_id)
            print('booking', booking)
            break 
        except booking_model.DoesNotExist:
            continue  
    
    if not booking:
        return HttpResponse("Invalid transaction ID", status=status.HTTP_400_BAD_REQUEST)

    # Handle payment status (either successful or failed)
    if payment_status == 'Successful':
        booking.payment_status = 'successful'
        if booking.total_amount == booking.advance_payable:
            booking.is_paid_full = True

        # Mark the appropriate slot as booked
        if hasattr(booking, 'turf_slot') and booking.turf_slot:
            booking.turf_slot.is_booked = True
            booking.turf_slot.save()
        elif hasattr(booking, 'badminton_slot') and booking.badminton_slot:
            booking.badminton_slot.is_booked = True
            booking.badminton_slot.save()
        elif hasattr(booking, 'swimming_slot') and booking.swimming_slot:
            booking.swimming_slot.is_booked = True
            booking.swimming_slot.save()

        booking.save()
        return HttpResponse('payment_success')
    

@csrf_exempt
def payment_failure(request):
    return HttpResponse('Payment Failed')



class Booking_history(viewsets.ReadOnlyModelViewSet):
    queryset = Booking_History.objects.all()
    serializer_class = Booking_HistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['booking_date','turf_book','badminton_book','swimming_book','turf','user']
    @action(detail=False, methods=['get'])
    def history_by_date(self, request):
        date = request.query_params.get('date')
        if not date:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        history = Booking_History.objects.filter(booking_date=date, user=request.user)
        serializer = Booking_HistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class MyBookingsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Turf_Booking.objects.none()  
    serializer_class = TurfBookingSerializer  

    def list(self, request, *args, **kwargs):
        user = request.user
        turf_bookings = Turf_Booking.objects.filter(user=user).order_by('-created_at')
        badminton_bookings = Badminton_Booking.objects.filter(user=user).order_by('-created_at')
        swimming_bookings = Swimming_Booking.objects.filter(user=user).order_by('-created_at')

        # Serializing each booking type
        turf_serializer = TurfBookingSerializer(turf_bookings, many=True, context={'request': request})
        badminton_serializer = BadmintonBookingSerializer(badminton_bookings, many=True, context={'request': request})
        swimming_serializer = SwimmingBookingSerializer(swimming_bookings, many=True, context={'request': request})

        # Returning the response with all booking data
        return Response({
            'turf_bookings': turf_serializer.data,
            'badminton_bookings': badminton_serializer.data,
            'swimming_bookings': swimming_serializer.data,
        })

    def get_queryset(self):
        return Turf_Booking.objects.filter(user=self.request.user)