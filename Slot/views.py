from rest_framework import viewsets,status
from .models import TurfSlot, BadmintonSlot, SwimmingSession, SwimmingSlot,SlotHistory,Coupon
from .serializers import TurfSlotSerializer, BadmintonSlotSerializer, SwimmingSessionSerializer,SlotHistorySerializer, SwimmingSlotSerializer
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from Booking.models import ApplyCoupon

class TurfSlotViewSet(viewsets.ModelViewSet):
    queryset = TurfSlot.objects.all()
    serializer_class = TurfSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','id']
    
    @action(detail=True, methods=['PATCH'])
    def apply_coupon(self, request, pk=None):
        print("apply_coupon view reached")  
        turf_slot = self.get_object()
        coupon_code = request.data.get('coupon_code')
        print(f"Slot id: {turf_slot}")  
        print(f"Coupon Code: {coupon_code}")  

        # Validate the coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            print(f"Coupon found: {coupon.code}")  # Debugging line
        except Coupon.DoesNotExist:
            print("Coupon not found")  # Debugging line
            return Response({'error': 'Invalid or inactive coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the original price and the new discounted price
        original_price = turf_slot.calculate_price()
        discount_amount = coupon.discount_amount
        discounted_price = original_price - discount_amount
        print(f"Original Price: {original_price}")  # Debugging line
        print(f"Discounted Price: {discounted_price}")  # Debugging line
        
        min_price = 500

        if discounted_price < min_price:
            print(f"Discounted price is too low: {discounted_price}. Coupon not applied.")  # Debugging line
            return Response({'error': f"The discount cannot be applied as the price is too low. Minimum price is {min_price}."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save the coupon application
        ApplyCoupon.objects.create(
            user=request.user,
            turf_slot=turf_slot,
            coupon=coupon,
            discount_applied=discount_amount
        )
        print("Coupon application saved")  # Debugging line

        # Update the total price of the TurfSlot
        turf_slot.discounted_price = discounted_price
        turf_slot.save()

        # Response data
        response_data = {
            'turf_slot_id': turf_slot.id,
            'original_price': turf_slot.calculate_price(),
            'coupon_code': coupon.code,
            'discount_amount': discount_amount,
            'discounted_price': discounted_price,
        }

        return Response(response_data, status=status.HTTP_200_OK)
   

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_instance = serializer.save()
        try:
            # Get the correct total price (check if coupon has been applied)
            if hasattr(slot_instance, 'discounted_price') and slot_instance.discounted_price:
                total_price = slot_instance.discounted_price
            else:
                total_price = slot_instance.calculate_price()
            SlotHistory.objects.create(
                user=request.user,
                turf_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            slot_instance.save() 
            
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_instance.id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
   

class BadmintonSlotViewSet(viewsets.ModelViewSet):
    queryset = BadmintonSlot.objects.all()
    serializer_class = BadmintonSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','id']
    @action(detail=True, methods=['PATCH'])
    def apply_coupon(self, request, pk=None):
        print("apply_coupon view reached")  
        Badminton_Slot = self.get_object()
        coupon_code = request.data.get('coupon_code')
        print(f"Slot id: {Badminton_Slot}")  
        print(f"Coupon Code: {coupon_code}")  

        # Validate the coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            print(f"Coupon found: {coupon.code}")  # Debugging line
        except Coupon.DoesNotExist:
            print("Coupon not found")  # Debugging line
            return Response({'error': 'Invalid or inactive coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the original price and the new discounted price
        original_price = Badminton_Slot.calculate_price()
        discount_amount = coupon.discount_amount
        discounted_price = original_price - discount_amount
        print(f"Original Price: {original_price}")  # Debugging line
        print(f"Discounted Price: {discounted_price}")  # Debugging line
        
        min_price = 400

        if discounted_price < min_price:
            print(f"Discounted price is too low: {discounted_price}. Coupon not applied.")  # Debugging line
            return Response({'error': f"The discount cannot be applied as the price is too low. Minimum price is {min_price}."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Save the coupon application
        ApplyCoupon.objects.create(
            user=request.user,
            Badminton_Slot=Badminton_Slot,
            coupon=coupon,
            discount_applied=discount_amount
        )
        print("Coupon application saved")  # Debugging line

        # Update the total price of the TurfSlot
        Badminton_Slot.discounted_price = discounted_price
        Badminton_Slot.save()

        # Response data
        response_data = {
            'Badminton_Slot_id': Badminton_Slot.id,
            'original_price': Badminton_Slot.calculate_price(),
            'coupon_code': coupon.code,
            'discount_amount': discount_amount,
            'discounted_price': discounted_price,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_instance = serializer.save()

        try:
            # Get the correct total price (check if coupon has been applied)
            if hasattr(slot_instance, 'discounted_price') and slot_instance.discounted_price:
                total_price = slot_instance.discounted_price
            else:
                total_price = slot_instance.calculate_price()
            SlotHistory.objects.create(
                user=request.user,
                badminton_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            slot_instance.save() 
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_instance.id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class SwimmingSessionViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSession.objects.all()
    serializer_class = SwimmingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def remaining_capacity(self, request, pk=None):
        session = self.get_object()
        date = request.query_params.get('date')

        if not date:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        remaining_capacity = session.remaining_capacity(date)
        return Response({'remaining_capacity': remaining_capacity}, status=status.HTTP_200_OK)
    
class SwimmingSlotViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSlot.objects.all()
    serializer_class = SwimmingSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    filterset_fields = ['user','id']
    @action(detail=True, methods=['PATCH'])
    def apply_coupon(self, request, pk=None):
        print("apply_coupon view reached")  
        Swimming_Slot = self.get_object()
        coupon_code = request.data.get('coupon_code')
        print(f"Slot id: {Swimming_Slot}")  
        print(f"Coupon Code: {coupon_code}")  

        # Validate the coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            print(f"Coupon found: {coupon.code}")  # Debugging line
        except Coupon.DoesNotExist:
            print("Coupon not found")  # Debugging line
            return Response({'error': 'Invalid or inactive coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the original price and the new discounted price
        original_price = Swimming_Slot.calculate_price()
        discount_amount = coupon.discount_amount
        discounted_price = original_price - discount_amount
        print(f"Original Price: {original_price}")  # Debugging line
        print(f"Discounted Price: {discounted_price}")  # Debugging line
        
        min_price = 400

        if discounted_price < min_price:
            print(f"Discounted price is too low: {discounted_price}. Coupon not applied.")  # Debugging line
            return Response({'error': f"The discount cannot be applied as the price is too low. Minimum price is {min_price}."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Save the coupon application
        ApplyCoupon.objects.create(
            user=request.user,
            Swimming_Slot=Swimming_Slot,
            coupon=coupon,
            discount_applied=discount_amount
        )
        print("Coupon application saved")  # Debugging line

        # Update the total price of the TurfSlot
        Swimming_Slot.discounted_price = discounted_price
        Swimming_Slot.save()

        # Response data
        response_data = {
            'Swimming_Slot_id': Swimming_Slot.id,
            'original_price': Swimming_Slot.calculate_price(),
            'coupon_code': coupon.code,
            'discount_amount': discount_amount,
            'discounted_price': discounted_price,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_instance = serializer.save()

        try:
            # Get the correct total price (check if coupon has been applied)
            if hasattr(slot_instance, 'discounted_price') and slot_instance.discounted_price:
                total_price = slot_instance.discounted_price
            else:
                total_price = slot_instance.calculate_price()
            SlotHistory.objects.create(
                user=request.user,
                swimming_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            slot_instance.save()
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_instance.id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SlotHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SlotHistory.objects.all()
    serializer_class = SlotHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'turf','booking_date','turf_slot','badminton_slot','swimming_slot']
    @action(detail=False, methods=['get'])
    def history_by_date(self, request):
        date = request.query_params.get('date')
        if not date:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        history = SlotHistory.objects.filter(booking_date=date, user=request.user)
        serializer = SlotHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
