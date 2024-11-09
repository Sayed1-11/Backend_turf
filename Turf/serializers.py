from rest_framework import serializers
from django.contrib import admin
from .models import Turf, Facility, Sports, SportField, TimeSlot, Price, SlotEligibility,Review
from Offers.models import Coupon
import requests
from User.models import UserModel
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id','name']



class SportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sports
        fields = ['id','name','image']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'turf', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

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
    facilities = FacilitySerializer(many=True ,required=False)   
    sports = SportsSerializer(many=True, required=False)
    fields = SportFieldSerializer(many=True, required=False)

    available_offers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Coupon.objects.all(), required=False
    )
    
    
    review_count = serializers.SerializerMethodField()
    class Meta:
        model = Turf
        fields = [
            'id','User', 'name', 'location','phone_number','latitude','longitude', 'image', 'facilities', 'sports',
            'available_offers', 'rating', 'fields','review_count'
        ]
        read_only_fields = ['rating','phone_number','latitude','longitude','review_count']

    def get_review_count(self, obj):
        return obj.reviews.count()

    def create(self, validated_data):
        # Extract Many-to-Many fields data with proper validation
        facilities_data = validated_data.pop('facilities', [])
        sports_data = validated_data.pop('sports', [])
        available_offers_data = validated_data.pop('available_offers', [])
        fields_data = validated_data.pop('fields', [])


        # Get latitude and longitude from location address
        lat, lon = self.get_lat_lon_from_address(validated_data.get('location'))
        validated_data['latitude'] = lat
        validated_data['longitude'] = lon

        user = self.context['request'].user
        validated_data['User'] = user
        validated_data['phone_number'] = user.phone_number
        
        # Create Turf instance
        turf = Turf.objects.create(**validated_data)
        if facilities_data:
            turf.facilities.set(facilities_data)
        if sports_data:
            turf.sports.set(sports_data)
        if available_offers_data:
            turf.available_offers.set(available_offers_data)

        # Create related SportField and Price instances
        for field_data in fields_data:
            SportField.objects.create(turf=turf, **field_data)

        return turf

    def update(self, instance, validated_data):
        location = validated_data.get('location', instance.location)
        if location and location != instance.location:
            lat, lon = self.get_lat_lon_from_address(location)
            instance.latitude = lat
            instance.longitude = lon

        facilities_data = validated_data.pop('facilities', [])
        sports_data = validated_data.pop('sports', [])
        available_offers_data = validated_data.pop('available_offers', [])
        fields_data = validated_data.pop('fields', [])

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.facilities.set(facilities_data)
        instance.sports.set(sports_data)
        instance.available_offers.set(available_offers_data)

        existing_field_ids = [field['id'] for field in fields_data if 'id' in field]
        SportField.objects.filter(turf=instance).exclude(id__in=existing_field_ids).delete()

        for field_data in fields_data:
            field_id = field_data.get('id')
            if field_id:
                field = SportField.objects.get(id=field_id, turf=instance)
                field.field_type = field_data.get('field_type', field.field_type)
                field.sport = field_data.get('sport', field.sport)
                field.width = field_data.get('width', field.width)
                field.height = field_data.get('height', field.height)
                field.save()
            else:
                SportField.objects.create(turf=instance, **field_data)

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
    
