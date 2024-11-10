from rest_framework import serializers
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking,Booking_History
from Slot.models import TurfSlot,SwimmingSlot,BadmintonSlot
from Turf.serializers import TurfSerializer
from Slot.serializers import TurfSlotSerializer,BadmintonSlotSerializer,SwimmingSlotSerializer,SwimmingSessionSerializer
from django.conf import settings

class TurfBookingSerializer(serializers.ModelSerializer): 
    turf = serializers.SerializerMethodField()
    turf_slot = TurfSlotSerializer(read_only=True)
    turf_slot_id = serializers.PrimaryKeyRelatedField(queryset=TurfSlot.objects.all(), write_only=True)
    class Meta:
        model = Turf_Booking
        fields = [
            'id', 'user', 'turf', 'turf_slot','turf_slot_id', 
            'coupon', 'discount', 'total_amount', 
            'advance_payable', 'due_amount', 'is_paid_full', 'status', 'created_at', 'order_id', 'transaction_id', 'payment_status'
        ]
        read_only_fields = ['total_amount', 'order_id', 'status', 'created_at', 'discount', 'due_amount', 'transaction_id', 'payment_status']

    def get_turf(self, obj):
        turf_instance = obj.turf_slot.turf if obj.turf_slot else None
        if turf_instance:
            request = self.context.get('request')
            if not request:
                print("Request context is missing in get_turf.")
            return TurfSerializer(turf_instance, context={'request': request}).data
        return None

    def validate(self, attrs):
        is_paid_full = attrs.get('is_paid_full', False)
        advance_payable = attrs.get('advance_payable', 500)

        turf_slot = attrs.get('turf_slot_id')
        print('turf_slot:',turf_slot.id)
        if turf_slot.id:
            try:
                turf_slot_instance = TurfSlot.objects.get(id=turf_slot.id)

                if Turf_Booking.objects.filter(turf_slot=turf_slot_instance).exists():
                    raise serializers.ValidationError("The selected turf slot is already booked during this time.")

                print('going')  
                total_amount = turf_slot_instance.calculate_price()
                attrs['total_amount'] = total_amount

                if is_paid_full:
                    if advance_payable < total_amount:
                        raise serializers.ValidationError("If 'is_paid_full' is true, you must pay the total amount.")
                    if advance_payable > total_amount:
                        raise serializers.ValidationError("You cannot pay more than the total amount.")
        
            except TurfSlot.DoesNotExist:
                raise serializers.ValidationError("The specified turf slot does not exist.")

        return attrs
    
    def create(self, validated_data):
        # Extract turf_slot_id from validated data
        turf_slot_id = validated_data.pop('turf_slot_id')

        try:
            turf_slot = TurfSlot.objects.get(id=turf_slot_id.id)  # Fetch TurfSlot using the ID
        except TurfSlot.DoesNotExist:
            raise serializers.ValidationError("The specified turf slot does not exist.")
        print(turf_slot.id)
        booking = Turf_Booking.objects.create(turf_slot=turf_slot, **validated_data)
        return booking
    
class BadmintonBookingSerializer(serializers.ModelSerializer):
    turf = serializers.SerializerMethodField() 
    badminton_slot = BadmintonSlotSerializer(read_only=True)
    badminton_slot_id = serializers.PrimaryKeyRelatedField(queryset=BadmintonSlot.objects.all(), write_only=True)
    class Meta:
        model = Badminton_Booking
        fields = [
            'id', 'user','turf','badminton_slot', 'badminton_slot_id',
            'coupon', 'discount', 'total_amount', 
            'advance_payable', 'due_amount', 'is_paid_full', 'status','created_at','order_id','transaction_id','payment_status'
        ]
        read_only_fields = ['total_amount','order_id', 'status','created_at', 'discount', 'due_amount','transaction_id','payment_status'] 
    def get_turf(self, obj):
        turf_instance = obj.badminton_slot.turf if obj.badminton_slot else None
        if turf_instance:
            request = self.context.get('request')
            if not request:
                print("Request context is missing in get_turf.")
            return TurfSerializer(turf_instance, context={'request': request}).data
        return None
    def validate(self, attrs):
        is_paid_full = attrs.get('is_paid_full', False)
        advance_payable = attrs.get('advance_payable', 200)
        badminton_slot = attrs.get('badminton_slot')

        if badminton_slot:
            try:
                badminton_slot_instance = BadmintonSlot.objects.get(id=badminton_slot.id)

                if Badminton_Booking.objects.filter(badminton_slot=badminton_slot_instance).exists():
                    raise serializers.ValidationError("The selected badminton slot is already booked during this time.")

                total_amount = badminton_slot_instance.calculate_price()
                attrs['total_amount'] = total_amount

                if is_paid_full:
                    if advance_payable < total_amount:
                        raise serializers.ValidationError("If 'is_paid_full' is true, you must pay the total amount.")
                    if advance_payable > total_amount:
                        raise serializers.ValidationError("You cannot pay more than the total amount.")

            except BadmintonSlot.DoesNotExist:
                raise serializers.ValidationError("The specified badminton slot does not exist.")

        return attrs
    

    def create(self, validated_data):
        # Extract turf_slot_id from validated data
        badminton_slot_id = validated_data.pop('badminton_slot_id')

        try:
            badminton_slot_instance  = BadmintonSlot.objects.get(id=badminton_slot_id.id)  # Fetch TurfSlot using the ID
        except BadmintonSlot.DoesNotExist:
            raise serializers.ValidationError("The specified turf slot does not exist.")
        print(badminton_slot_instance .id)
        booking = Badminton_Booking.objects.create(badminton_slot=badminton_slot_instance , **validated_data)

        print('booked')
        return booking
class SwimmingBookingSerializer(serializers.ModelSerializer):
    turf = serializers.SerializerMethodField()
    swimming_slot = SwimmingSlotSerializer(read_only=True)
    swimming_slot_id = serializers.PrimaryKeyRelatedField(queryset=SwimmingSlot.objects.all(), write_only=True)
    swimming_session = SwimmingSessionSerializer(source="swimming_slot.session", read_only=True)
    class Meta:
        model = Swimming_Booking
        fields = [
            'id', 'user', 'turf','swimming_slot', 'swimming_session','swimming_slot_id',
            'coupon', 'discount', 'total_amount', 
           'due_amount', 'is_paid_full', 'status','created_at','advance_payable','order_id','transaction_id','payment_status'
        ]
        read_only_fields = ['total_amount','order_id', 'discount', 'total_amount', 
           'due_amount', 'is_paid_full', 'status','created_at','transaction_id','payment_status']  
    def get_turf(self, obj):
        turf_instance = obj.swimming_slot.turf if obj.swimming_slot else None
        if turf_instance:
            request = self.context.get('request')
            if not request:
                print("Request context is missing in get_turf.")
            return TurfSerializer(turf_instance, context={'request': request}).data
        return None
    
    def validate(self, attrs):
        is_paid_full = attrs.get('is_paid_full', False)
        advance_payable = attrs.get('advance_payable', 0)
        
        swimming_slot = attrs.get('swimming_slot')

        if swimming_slot:
            try:
   
                swimming_slot_instance = SwimmingSlot.objects.get(id=swimming_slot.id)

                if Swimming_Booking.objects.filter(swimming_slot=swimming_slot_instance).exists():
                     if swimming_slot_instance.available_capacity() <= 0:
                         raise serializers.ValidationError("The selected swimming session is fully booked.")

                total_amount = swimming_slot_instance.calculate_price()
                attrs['total_amount'] = total_amount

                if is_paid_full:
                    if advance_payable < total_amount:
                        raise serializers.ValidationError("If 'is_paid_full' is true, you must pay the total amount.")
                    if advance_payable > total_amount:
                        raise serializers.ValidationError("You cannot pay more than the total amount.")
        
            except SwimmingSlot.DoesNotExist:
                raise serializers.ValidationError("The specified turf slot does not exist.")

        return attrs

    def create(self, validated_data):
        # Extract turf_slot_id from validated data
        swimming_slot_id = validated_data.pop('swimming_slot_id')

        try:
            Swimming_slot_instance = SwimmingSlot.objects.get(id=swimming_slot_id.id)  # Fetch TurfSlot using the ID
        except SwimmingSlot.DoesNotExist:
            raise serializers.ValidationError("The specified turf slot does not exist.")
        print(Swimming_slot_instance.id)
        booking = Swimming_Booking.objects.create(swimming_slot=Swimming_slot_instance, **validated_data)

        print('booked')
        return booking
class Booking_HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking_History
        fields = ['id','turf_book', 'booking_date','badminton_book','swimming_book', 'total_price','advance_payable']
