from rest_framework import serializers
from .models import TurfSlot, BadmintonSlot, SwimmingSession, SwimmingSlot,SlotHistory
from Turf.models import Turf,Price

class TurfSlotSerializer(serializers.ModelSerializer):
    calculated_price = serializers.SerializerMethodField()
    class Meta:
        model = TurfSlot
        fields = ['id', 'user', 'turf', 'field', 'start_time', 'end_time', 'date', 
                  'is_booked', 'is_available', 'coupon', 'sports', 'calculated_price']
        
        read_only_fields = ['is_booked', 'is_available', 'calculated_price']
    def get_calculated_price(self, obj):
        try:
            return obj.calculate_price() 
        except Exception as e:
            return str(e) 
    def validate(self, attrs):
        turf = attrs.get('turf')
        field = attrs.get('field')

        if turf and field:
            try:
                turf_instance = Turf.objects.get(id=turf.id)
                if field not in turf_instance.fields.all():
                    raise serializers.ValidationError("The selected field does not belong to the specified turf.")

            except Turf.DoesNotExist:
                raise serializers.ValidationError("The specified turf does not exist.")

        return attrs
  

class BadmintonSlotSerializer(serializers.ModelSerializer):
    calculated_price = serializers.SerializerMethodField()
    class Meta:
        model = BadmintonSlot
        fields = ['id', 'user', 'turf', 'field', 'start_time', 'end_time', 'date', 
                  'is_booked', 'is_available', 'coupon', 'calculated_price']
        read_only_fields = ['is_booked', 'is_available', 'calculated_price']
    def get_calculated_price(self, obj):
        try:
            return obj.calculate_price() 
        except Exception as e:
            return str(e)
    
    def validate(self, attrs):
        turf = attrs.get('turf')
        field = attrs.get('field')

        if turf and field:
            try:
                turf_instance = Turf.objects.get(id=turf.id)
                if field not in turf_instance.fields.all():
                    raise serializers.ValidationError("The selected field does not belong to the specified turf.")

            except Turf.DoesNotExist:
                raise serializers.ValidationError("The specified turf does not exist.")

        return attrs

class SwimmingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwimmingSession
        fields = ['id', 'start_time', 'end_time', 'capacity', 'price_per_person']

class SwimmingSlotSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=SwimmingSession.objects.all())
    calculated_price = serializers.SerializerMethodField()
    class Meta:
        model = SwimmingSlot
        fields = ['id', 'user', 'turf', 'field', 'date', 'is_booked', 'coupon', 'session', 'number_of_people','calculated_price']
        read_only_fields = ['is_booked', 'calculated_price']
    def get_calculated_price(self, obj):
        try:
            return obj.calculate_price() 
        except Exception as e:
            return str(e)
        
    def validate(self, attrs):
        turf = attrs.get('turf')
        field = attrs.get('field')

        if turf and field:
            try:
                turf_instance = Turf.objects.get(id=turf.id)
                if field not in turf_instance.fields.all():
                    raise serializers.ValidationError("The selected field does not belong to the specified turf.")

            except Turf.DoesNotExist:
                raise serializers.ValidationError("The specified turf does not exist.")

        return attrs
    
class SlotHistorySerializer(serializers.ModelSerializer):
    turf_slot = TurfSlotSerializer(read_only=True)
    badminton_slot = BadmintonSlotSerializer(read_only=True)
    swimming_slot = SwimmingSlotSerializer(read_only=True)
    
    class Meta:
        model = SlotHistory
        fields = ['id', 'user', 'turf_slot', 'badminton_slot', 'swimming_slot', 'booking_date', 'total_price', 'turf']
