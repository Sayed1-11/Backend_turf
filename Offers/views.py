from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Coupon
from .serializers import CouponSerializer
from rest_framework.exceptions import ValidationError

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]  
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'discount_amount', 'is_active']
    ordering = ['-id']  
    def perform_create(self, serializer):
        if serializer.validated_data['discount_amount'] <= 0:
            raise ValidationError("Discount amount must be greater than zero.")
        super().perform_create(serializer)
