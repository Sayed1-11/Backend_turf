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
    
class CouponValidationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20, required=True)

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_active:
                raise serializers.ValidationError("This coupon is not active.")
            return coupon  # Returning the coupon object for additional usage if needed
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")