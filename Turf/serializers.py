from rest_framework import serializers
from django.contrib import admin
from .models import Turf, Facility, Sports, SportField, TimeSlot, Price, SlotEligibility
from Offers.models import Coupon
import requests
from User.models import UserModel
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['name']



class SportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sports
        fields = ['name']



class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id','turf', 'start_time', 'end_time', 'duration']


class PriceSerializer(serializers.ModelSerializer):
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    
    class Meta:
        model = Price
        fields = ['id','turf', 'field', 'time_slot', 'price_per_hour', 'duration_hours','days_of_week'] 
        unique_together = ('field', 'time_slot', 'duration_hours')
        read_only_fields = ['currency']
    def validate(self, attrs):
        
        field = attrs.get('field')
        time_slot = attrs.get('time_slot')
        duration_hours = attrs.get('duration_hours')
        days_of_week = attrs.get('days_of_week')

        if Price.objects.filter(field=field, time_slot=time_slot, duration_hours=duration_hours, days_of_week=days_of_week).exists():
            raise serializers.ValidationError("A price with this time slot, duration, and day of the week already exists for this field.")
        
        return attrs
    def create(self, validated_data):
 
        field_instance = validated_data['field']
        validated_data['turf'] = field_instance.turf  
        return super().create(validated_data)

    def update(self, instance, validated_data):

        instance.time_slot = validated_data.get('time_slot', instance.time_slot)
        instance.price_per_hour = validated_data.get('price_per_hour', instance.price_per_hour)
        instance.duration_hours = validated_data.get('duration_hours', instance.duration_hours)
        instance.save()
        return instance
    
class SportFieldSerializer(serializers.ModelSerializer):
    sport = serializers.PrimaryKeyRelatedField(queryset=Sports.objects.all())  
    
    class Meta:
        model = SportField
        fields = ['id','turf', 'field_type', 'sport', 'width', 'height']
    def __init__(self, *args, **kwargs):
        turf_id = kwargs['data'].get('turf') if 'data' in kwargs else None  
        super(SportFieldSerializer, self).__init__(*args, **kwargs)

        if turf_id:
            try:
                turf_instance = Turf.objects.get(id=turf_id)
                self.fields['sport'].queryset = turf_instance.sports.all()
            except Turf.DoesNotExist:
                self.fields['sport'].queryset = Sports.objects.none()
    def validate_sport(self, value):
      
        turf = self.initial_data.get('turf')
        if turf:
            try:
                turf_instance = Turf.objects.get(id=turf)
                if value not in turf_instance.sports.all():
                    raise serializers.ValidationError("The selected sport is not available for this turf.")
            except Turf.DoesNotExist:
                raise serializers.ValidationError("Turf does not exist.")
        return value

    def create(self, validated_data):
        sport_field = SportField.objects.create(**validated_data)
        return sport_field

    def update(self, instance, validated_data):
        instance.field_type = validated_data.get('field_type', instance.field_type)
        instance.sport = validated_data.get('sport', instance.sport)
        instance.width = validated_data.get('width', instance.width)
        instance.height = validated_data.get('height', instance.height)
        instance.save()


        return instance


class SlotEligibilitySerializer(serializers.ModelSerializer):
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())

    class Meta:
        model = SlotEligibility
        fields = ['id','Turf', 'time_slot', 'is_available', 'reason']


class TurfSerializer(serializers.ModelSerializer):
    User = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())
    facilities = FacilitySerializer(many=True)  
    time_slots = TimeSlotSerializer(many=True)  
    sports = SportsSerializer(many=True)
    fields = SportFieldSerializer(many=True, required=False)
    prices = PriceSerializer(many=True, required=False, source='price_set') 
    slot_eligibilities = SlotEligibilitySerializer(many=True, required=False)
    available_offers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Coupon.objects.all(), required=False
    )

    class Meta:
        model = Turf
        fields = [
            'id','User', 'name', 'location','phone_number', 'image', 'facilities', 'sports',
            'available_offers', 'rating', 'fields', 'prices', 'slot_eligibilities','time_slots',
        ]
        read_only_fields = ['rating','phone_number']
    def create(self, validated_data):
        # Extract Many-to-Many fields data
        facilities_data = validated_data.pop('facilities', [])
        sports_data = validated_data.pop('sports', [])
        available_offers_data = validated_data.pop('available_offers', [])
        fields_data = validated_data.pop('fields', [])
        slot_eligibilities_data = validated_data.pop('slot_eligibilities', [])
        lat, lon = self.get_lat_lon_from_address(validated_data.get('location'))
        validated_data['latitude'] = lat
        validated_data['longitude'] = lon
        user = self.context['request'].user
        validated_data['User'] = user
        validated_data['phone_number'] = user.phone_number
        turf = Turf.objects.create(**validated_data)

        turf.facilities.set(facilities_data)
        turf.sports.set(sports_data)
        turf.available_offers.set(available_offers_data)


        for field_data in fields_data:
            prices_data = field_data.pop('prices', [])
            field = SportField.objects.create(turf=turf, **field_data)
            for price_data in prices_data:
                Price.objects.create(field=field, **price_data)

        for slot_data in slot_eligibilities_data:
            SlotEligibility.objects.create(turf=turf, **slot_data)

        return turf

    def update(self, instance, validated_data):
        location = validated_data.get('location', instance.location)
        if location and location != instance.location:
            lat, lon = self.get_lat_lon_from_address(location)
            instance.latitude = lat
            instance.longitude = lon

        fields_data = validated_data.pop('fields', [])
        slot_eligibilities_data = validated_data.pop('slot_eligibilities', [])

        facilities_data = validated_data.pop('facilities', [])
        sports_data = validated_data.pop('sports', [])

        instance.name = validated_data.get('name', instance.name)
        
        
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.facilities.set(facilities_data)
        instance.sports.set(sports_data)

        available_offers_data = validated_data.pop('available_offers', [])
        instance.available_offers.set(available_offers_data)

        for field_data in fields_data:
            prices_data = field_data.pop('prices', [])
            field_id = field_data.get('id')

            if field_id:

                field = SportField.objects.get(id=field_id, turf=instance)
                field.field_type = field_data.get('field_type', field.field_type)
                field.sport = field_data.get('sport', field.sport)
                field.width = field_data.get('width', field.width)
                field.height = field_data.get('height', field.height)
                field.save()


                for price_data in prices_data:
                    price_id = price_data.get('id')
                    if price_id:
                        price = Price.objects.get(id=price_id, field=field)
                        price.price_per_hour = price_data.get('price_per_hour', price.price_per_hour)
                        price.duration_hours = price_data.get('duration_hours', price.duration_hours)
                        price.save()
                    else:
                        Price.objects.create(field=field, **price_data)
            else:
                field = SportField.objects.create(turf=instance, **field_data)
                for price_data in prices_data:
                    Price.objects.create(field=field, **price_data)

        for slot_data in slot_eligibilities_data:
            slot_id = slot_data.get('id')
            if slot_id:
                slot = SlotEligibility.objects.get(id=slot_id, turf=instance)
                slot.is_available = slot_data.get('is_available', slot.is_available)
                slot.reason = slot_data.get('reason', slot.reason)
                slot.save()
            else:
                SlotEligibility.objects.create(turf=instance, **slot_data)

        return instance

    def get_lat_lon_from_address(self, address):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            response_data = response.json()

            if response_data:
                lat = response_data[0].get("lat")
                lon = response_data[0].get("lon")
                return lat, lon

        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None, None    