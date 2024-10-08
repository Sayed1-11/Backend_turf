from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Turf, Sports, TimeSlot, Price,SportField,Facility,SlotEligibility
from .serializers import TurfSerializer, SportsSerializer, TimeSlotSerializer, PriceSerializer,SportFieldSerializer,FacilitySerializer,SlotEligibilitySerializer
from rest_framework.views import APIView

class TurfViewSet(viewsets.ModelViewSet):
    queryset = Turf.objects.all()
    serializer_class = TurfSerializer

    def get_queryset(self):
        # Prefetch related fields to optimize database queries
        return Turf.objects.prefetch_related(
            'facilities', 'sports', 'fields', 'fields__prices', 'slot_eligibilities'
        ).all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name')
        location = request.query_params.get('location')

        queryset = self.get_queryset()
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if location:
            queryset = queryset.filter(location__icontains=location)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# ViewSet for Sports
class SportsViewSet(viewsets.ModelViewSet):
    queryset = Sports.objects.all()
    serializer_class = SportsSerializer
    
class FacilitiesViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer

class SportFieldViewSet(viewsets.ModelViewSet):
    queryset = SportField.objects.all()
    serializer_class = SportFieldSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
# ViewSet for TimeSlot
class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
class TimeSlotEligibilityViewSet(viewsets.ModelViewSet):
    queryset = SlotEligibility.objects.all()
    serializer_class = SlotEligibilitySerializer

# ViewSet for Price
class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer

class FieldTypeChoicesView(APIView):
    def get(self, request):
        choices = SportField.FIELD_TYPE_CHOICES
        return Response({'field_types': choices})