from rest_framework import viewsets,status
from .models import TurfSlot, BadmintonSlot, SwimmingSession, SwimmingSlot,SlotHistory
from .serializers import TurfSlotSerializer, BadmintonSlotSerializer, SwimmingSessionSerializer, SwimmingSlotSerializer,SlotHistorySerializer
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

class TurfSlotViewSet(viewsets.ModelViewSet):
    queryset = TurfSlot.objects.all()
    serializer_class = TurfSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_id = serializer.data['id']
        slot_instance = serializer.save()
        try:
            total_price = slot_instance.calculate_price()
            print("Prices: ", total_price)
            print('\n')
            slot_instance.is_available = False
            slot_instance.save()
            
            SlotHistory.objects.create(
                user=request.user,
                turf_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BadmintonSlotViewSet(viewsets.ModelViewSet):
    queryset = BadmintonSlot.objects.all()
    serializer_class = BadmintonSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_id = serializer.data['id']
        slot_instance = serializer.save()

        try:
            total_price = slot_instance.calculate_price()
            print("Prices: ", total_price)
            print('\n')
            slot_instance.is_available = False
            slot_instance.save()
            SlotHistory.objects.create(
                user=request.user,
                turf_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class SwimmingSessionViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSession.objects.all()
    serializer_class = SwimmingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def remaining_capacity(self, request, pk=None):
        session = self.get_object()
        date = request.query_params.get('date')

        if not date:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        remaining_capacity = session.remaining_capacity(date)
        return Response({'remaining_capacity': remaining_capacity}, status=status.HTTP_200_OK)
    
class SwimmingSlotViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSlot.objects.all()
    serializer_class = SwimmingSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    filterset_fields = ['user']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_id = serializer.data['id']
        slot_instance = serializer.save()

        try:
            total_price = slot_instance.calculate_price()
            print("Prices: ", total_price)
            print('\n')
            slot_instance.save()
            SlotHistory.objects.create(
                user=request.user,
                turf_slot=slot_instance,
                booking_date=slot_instance.date,
                total_price=total_price
            )
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price,'slot_id': slot_id}, status=status.HTTP_201_CREATED)
            
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SlotHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SlotHistory.objects.all()
    serializer_class = SlotHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'booking_date']
    @action(detail=False, methods=['get'])
    def history_by_date(self, request):
        date = request.query_params.get('date')
        if not date:
            return Response({'error': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        history = SlotHistory.objects.filter(booking_date=date, user=request.user)
        serializer = SlotHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
