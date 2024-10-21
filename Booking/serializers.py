from rest_framework import serializers
from .models import Turf_Booking, Badminton_Booking, Swimming_Booking
from Slot.models import TurfSlot,SwimmingSlot,BadmintonSlot
import requests,usaddress,logging
from django.conf import settings
class TurfBookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Turf_Booking
        fields = [
            'id', 'user','turf_slot', 
            'coupon', 'discount', 'total_amount', 
            'advance_payable', 'due_amount', 'is_paid_full', 'status','created_at','order_id','transaction_id','payment_status'
        ]
        read_only_fields = ['total_amount','order_id', 'status','created_at', 'discount', 'due_amount','transaction_id','payment_status'] 
    def validate(self, attrs):
        is_paid_full = attrs.get('is_paid_full', False)
        advance_payable = attrs.get('advance_payable', 0)

        turf_slot = attrs.get('turf_slot')

        if turf_slot:
            try:
                turf_slot_instance = TurfSlot.objects.get(id=turf_slot.id)


                if Turf_Booking.objects.filter(turf_slot=turf_slot_instance).exists():
                    raise serializers.ValidationError("The selected turf slot is already booked during this time.")

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
    
class BadmintonBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badminton_Booking
        fields = [
            'id', 'user','badminton_slot', 
            'coupon', 'discount', 'total_amount', 
            'advance_payable', 'due_amount', 'is_paid_full', 'status','created_at','order_id','transaction_id','payment_status'
        ]
        read_only_fields = ['total_amount','order_id', 'status','created_at', 'discount', 'due_amount','transaction_id','payment_status'] 
    def validate(self, attrs):
        is_paid_full = attrs.get('is_paid_full', False)
        advance_payable = attrs.get('advance_payable', 0)
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
class SwimmingBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Swimming_Booking
        fields = [
            'id', 'user', 'swimming_slot', 
            'coupon', 'discount', 'total_amount', 
           'due_amount', 'is_paid_full', 'status','created_at','advance_payable','order_id','transaction_id','payment_status'
        ]
        read_only_fields = ['total_amount','order_id', 'discount', 'total_amount', 
           'due_amount', 'is_paid_full', 'status','created_at','transaction_id','payment_status']  
    
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