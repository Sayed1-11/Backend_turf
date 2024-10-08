from rest_framework import viewsets,status
from .models import TurfSlot, BadmintonSlot, SwimmingSession, SwimmingSlot
from .serializers import TurfSlotSerializer, BadmintonSlotSerializer, SwimmingSessionSerializer, SwimmingSlotSerializer
from rest_framework.response import Response
from django.core.exceptions import ValidationError
class TurfSlotViewSet(viewsets.ModelViewSet):
    queryset = TurfSlot.objects.all()
    serializer_class = TurfSlotSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the slot instance after validation
        slot_instance = serializer.save()

        try:
            # Calculate the price for the booking
            total_price = slot_instance.calculate_price()
            print("Prices: ", total_price)
            print('\n')
            slot_instance.is_booked = True
            slot_instance.save()
            return Response({'message': 'Slot booked successfully!', 'total_price': total_price}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BadmintonSlotViewSet(viewsets.ModelViewSet):
    queryset = BadmintonSlot.objects.all()
    serializer_class = BadmintonSlotSerializer

class SwimmingSessionViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSession.objects.all()
    serializer_class = SwimmingSessionSerializer

class SwimmingSlotViewSet(viewsets.ModelViewSet):
    queryset = SwimmingSlot.objects.all()
    serializer_class = SwimmingSlotSerializer
