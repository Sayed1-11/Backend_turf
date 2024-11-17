from rest_framework import viewsets, filters,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Coupon
from .serializers import CouponSerializer,CouponValidationSerializer
from rest_framework.exceptions import ValidationError


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]  # Only admins can modify coupons
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'discount_amount', 'is_active']
    ordering = ['-id']  
    def perform_create(self, serializer):
        if serializer.validated_data['discount_amount'] <= 0:
            raise ValidationError("Discount amount must be greater than zero.")
        super().perform_create(serializer)

    @action(detail=False, methods=['post'])
    def validate(self, request):
        serializer = CouponValidationSerializer(data=request.data)
        if serializer.is_valid():
            coupon = serializer.validated_data['code']
            return Response({
                "message": "Coupon is valid.",
                "coupon_details": {
                    "id":coupon.id,
                    "name": coupon.name,
                    "code": coupon.code,
                    "discount_amount": coupon.discount_amount,
                    "description": coupon.description,
                    "issued_by": coupon.issued_by,
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
