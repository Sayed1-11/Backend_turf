from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'name', 'code', 'discount_amount', 'description', 'is_active', 'issued_by']
    
    def validate(self, attrs):
        if not attrs.get('is_active', True):
            raise serializers.ValidationError("This coupon is inactive and cannot be applied.")
        return attrs
    
