from rest_framework import serializers
from django.contrib import admin
from .models import Turf, Facility, Sports, SportField, TimeSlot, Price, SlotEligibility
from Offers.models import Coupon
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name']


# Serializer for Sports
class SportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sports
        fields = ['id', 'name']


# Serializer for TimeSlot
class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'duration']


class PriceSerializer(serializers.ModelSerializer):
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    
    class Meta:
        model = Price
        fields = ['id', 'field', 'time_slot', 'price_per_hour', 'duration_hours']  # Only include necessary fields
        read_only_fields = ['currency']
    def validate(self, attrs):
        """
        Validate that there are no existing prices for the same field
        and time slot with the same duration hours combination.
        """
        field = attrs.get('field')
        time_slot = attrs.get('time_slot')
        duration_hours = attrs.get('duration_hours')

        # Check for existing prices with the same field, time_slot, and duration_hours
        if Price.objects.filter(field=field, time_slot=time_slot, duration_hours=duration_hours).exists():
            raise serializers.ValidationError("A price with this time slot and duration already exists for this field.")

        return attrs
    def create(self, validated_data):
        # Set the turf based on the field provided
        field_instance = validated_data['field']
        validated_data['turf'] = field_instance.turf  # Set turf from the related field
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update the instance fields
        instance.time_slot = validated_data.get('time_slot', instance.time_slot)
        instance.price_per_hour = validated_data.get('price_per_hour', instance.price_per_hour)
        instance.duration_hours = validated_data.get('duration_hours', instance.duration_hours)
        instance.save()
        return instance
    
class SportFieldSerializer(serializers.ModelSerializer):
    sport = serializers.PrimaryKeyRelatedField(queryset=Sports.objects.all())  
    
    class Meta:
        model = SportField
        fields = ['id', 'turf', 'field_type', 'sport', 'width', 'height']
    def __init__(self, *args, **kwargs):
        turf_id = kwargs['data'].get('turf') if 'data' in kwargs else None  # Get turf from input data
        super(SportFieldSerializer, self).__init__(*args, **kwargs)

        if turf_id:
            try:
                turf_instance = Turf.objects.get(id=turf_id)
                # Filter the queryset for the sport field based on the associated turf's sports
                self.fields['sport'].queryset = turf_instance.sports.all()
            except Turf.DoesNotExist:
                self.fields['sport'].queryset = Sports.objects.none()
    def validate_sport(self, value):
        """
        Validate that the sport is available for the selected turf.
        """
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
        # Create the SportField instance
        sport_field = SportField.objects.create(**validated_data)
        return sport_field

    def update(self, instance, validated_data):
        instance.field_type = validated_data.get('field_type', instance.field_type)
        instance.sport = validated_data.get('sport', instance.sport)
        instance.width = validated_data.get('width', instance.width)
        instance.height = validated_data.get('height', instance.height)
        instance.save()

        # Handle price updates separately if needed
        # You can call a separate serializer or method here to handle prices if necessary

        return instance

# Serializer for SlotEligibility
class SlotEligibilitySerializer(serializers.ModelSerializer):
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())

    class Meta:
        model = SlotEligibility
        fields = ['id', 'Turf', 'time_slot', 'is_available', 'reason']


# Serializer for Turf
class TurfSerializer(serializers.ModelSerializer):
    facilities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Facility.objects.all()
    )
    sports = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Sports.objects.all()
    )
    fields = SportFieldSerializer(many=True, required=False)
    prices = PriceSerializer(many=True, required=False, source='price_set')  # Use price_set as the reverse relation
    slot_eligibilities = SlotEligibilitySerializer(many=True, required=False)
    available_offers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Coupon.objects.all(), required=False
    )

    class Meta:
        model = Turf
        fields = [
            'id', 'name', 'location', 'image','phone_number', 'facilities', 'sports',
            'available_offers', 'rating', 'fields', 'prices', 'slot_eligibilities',
        ]
        read_only_fields = ['rating']
    def create(self, validated_data):
        # Extract Many-to-Many fields data
        facilities_data = validated_data.pop('facilities', [])
        sports_data = validated_data.pop('sports', [])
        available_offers_data = validated_data.pop('available_offers', [])
        fields_data = validated_data.pop('fields', [])
        slot_eligibilities_data = validated_data.pop('slot_eligibilities', [])

        # Create the Turf instance without M2M fields
        turf = Turf.objects.create(**validated_data)

        # Set Many-to-Many relationships
        turf.facilities.set(facilities_data)
        turf.sports.set(sports_data)
        turf.available_offers.set(available_offers_data)

        # Create related SportField and Price instances
        for field_data in fields_data:
            prices_data = field_data.pop('prices', [])
            field = SportField.objects.create(turf=turf, **field_data)
            for price_data in prices_data:
                Price.objects.create(field=field, **price_data)

        # Create related SlotEligibility instances
        for slot_data in slot_eligibilities_data:
            SlotEligibility.objects.create(turf=turf, **slot_data)

        return turf

def update(self, instance, validated_data):
    fields_data = validated_data.pop('fields', [])
    slot_eligibilities_data = validated_data.pop('slot_eligibilities', [])

    facilities_data = validated_data.pop('facilities', [])
    sports_data = validated_data.pop('sports', [])

    # Update the turf instance fields
    instance.name = validated_data.get('name', instance.name)
    instance.location = validated_data.get('location', instance.location)
    instance.image = validated_data.get('image', instance.image)
    instance.save()

    # Update many-to-many relationships
    instance.facilities.set(facilities_data)
    instance.sports.set(sports_data)

    # Update available_offers using set()
    available_offers_data = validated_data.pop('available_offers', [])
    instance.available_offers.set(available_offers_data)

    # Update fields and related prices
    for field_data in fields_data:
        prices_data = field_data.pop('prices', [])
        field_id = field_data.get('id')

        if field_id:
            # Update existing field
            field = SportField.objects.get(id=field_id, turf=instance)
            field.field_type = field_data.get('field_type', field.field_type)
            field.sport = field_data.get('sport', field.sport)
            field.width = field_data.get('width', field.width)
            field.height = field_data.get('height', field.height)
            field.save()

            # Update related prices
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
            # Create new field if no ID is provided
            field = SportField.objects.create(turf=instance, **field_data)
            for price_data in prices_data:
                Price.objects.create(field=field, **price_data)

    # Update slot eligibilities
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
