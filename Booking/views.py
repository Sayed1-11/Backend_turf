from rest_framework import viewsets,filters
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking,Booking_History
from .serializers import (
    TurfBookingSerializer,
    BadmintonBookingSerializer,
    SwimmingBookingSerializer,
    Booking_HistorySerializer,
)
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
        customer_mobile = request.user.phone_number  # Get mobile from request or use a default
        booking_id = request.session.get('booking_id') # Get mobile from request or use a default
        print('booking_id',booking_id)
        success_url = f'http://127.0.0.1:8000/payment/success/{booking_id}/'
        
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl=success_url,  # Replace with actual success URL
            failUrl='https://backend-turf.onrender.com/payment/failure/',  # Replace with actual failure URL
            cancelUrl='https://backend-turf.onrender.com/payment/callback/',   # Replace with actual cancel URL
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
        payment_url = pay.payment()
        if not payment_url:
            logging.error("Payment URL not found during payment initiation.")
            booking.delete()  # Optionally delete the booking if payment initiation fails
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(f"Payment URL: {payment_url}")
        return Response({'payment_url': payment_url,'transaction id':transaction_id}, status=status.HTTP_200_OK)
def trigger_callback(booking):
        """
        Trigger the payment callback for a specific booking using its transaction_id.
        """
        transaction_id = booking.transaction_id  # Assuming transaction_id exists on booking model
        callback_url = "https://backend-turf.onrender.com/payment/callback/"
        params = {
            'mer_txnid': transaction_id,
            'pay_status': 'Successful',
        }

        # Make the HTTP POST request to the callback URL
        try:
            response = requests.post(callback_url, params=params)
            if response.status_code == 200:
                print(f"Successfully triggered callback for transaction ID: {transaction_id}")
            else:
                print(f"Error calling callback URL: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling callback URL: {e}")
                    
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

        # Retrieve customer details (e.g., from user profile or request)
        customer_name = request.user.phone_number or "John Doe"
        customer_email = request.user.email or "john.doe@example.com"
        customer_mobile = request.user.phone_number  

        # Initiating Aamarpay payment
        pay = aamarPay(
            isSandbox=True,  # Set to True for sandbox/testing mode
            storeID=settings.AAMARPAY_STORE_ID,  # Your actual store ID
            successUrl='https://backend-turf.onrender.com/payment/success/?transaction_id={transaction_id}',  # Replace with actual success URL
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
        swimming_slot = BadmintonSlot.objects.get(id=swimming_slot_id)
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
        return Response({'payment_url': payment_url,'transaction id':transaction_id}, status=status.HTTP_200_OK)

@csrf_exempt
def aamarpay_callback(request,transaction_id):
    if not transaction_id:
        logging.error("Missing transaction ID in callback.")
        return HttpResponse("Missing transaction ID", status=status.HTTP_400_BAD_REQUEST)

    booking = None
    for booking_model in [Turf_Booking, Badminton_Booking, Swimming_Booking]:
        try:
            booking = booking_model.objects.get(transaction_id=transaction_id)
            break 
        except booking_model.DoesNotExist:
            continue  
    if not booking:
        logging.error(f"Booking not found for transaction ID: {transaction_id}")
        return HttpResponse("Invalid transaction ID", status=status.HTTP_400_BAD_REQUEST)

    payment_status = request.GET.get('pay_status')

    if payment_status == 'Successful':
        booking.payment_status = 'successful'
        if booking.total_amount == booking.advance_payable:
            booking.is_paid_full = True
        booking.save() 
        logging.info(f"Payment successful for transaction ID: {transaction_id}")
        return redirect('payment_success')  
    else:
        booking.payment_status = 'failed'
        booking.save()
        logging.warning(f"Payment failed for transaction ID: {transaction_id}")
        return redirect('payment_failure')  
        
@csrf_exempt
def payment_success(request, booking_id):
    # booking_id is passed in the URL parameter
    print(f"Booking ID from URL: {booking_id}")

    session_booking_id = request.session.get('booking_id')
    print(f"Booking ID from session: {session_booking_id}")

    # Validate the booking_id
    if not booking_id:
        if not session_booking_id:
            return HttpResponse("Booking ID is required", status=400)
        booking_id = session_booking_id

    # Retrieve the booking from the database
    booking = None
    for model, model_name in [(Turf_Booking, 'turf'), (Badminton_Booking, 'badminton'), (Swimming_Booking, 'swimming')]:
        try:
            booking = model.objects.get(id=booking_id)
            break
        except model.DoesNotExist:
            continue

    if not booking:
        return HttpResponse("Booking not found", status=400)

    # Trigger the callback function for the booking
    trigger_callback(booking)

    # Clean up session by removing the booking_id after it is used
    if 'booking_id' in request.session:
        del request.session['booking_id']

    return HttpResponse("Payment Successful")

@csrf_exempt
def payment_failure(request):
    return HttpResponse("Payment Failled")



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
    

class MyBookingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        turf_bookings = Turf_Booking.objects.filter(user=user).order_by('-created_at')
        badminton_bookings = Badminton_Booking.objects.filter(user=user).order_by('-created_at')
        swimming_bookings = Swimming_Booking.objects.filter(user=user).order_by('-created_at')

        turf_serializer = TurfBookingSerializer(turf_bookings, many=True)
        badminton_serializer = BadmintonBookingSerializer(badminton_bookings, many=True)
        swimming_serializer = SwimmingBookingSerializer(swimming_bookings, many=True)

        return Response({
            'turf_bookings': turf_serializer.data,
            'badminton_bookings': badminton_serializer.data,
            'swimming_bookings': swimming_serializer.data,
        })
