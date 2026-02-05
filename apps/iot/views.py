from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Device, SensorData
from .serializers import (
    DeviceSerializer, 
    SensorDataSerializer, 
    SensorDataIngestSerializer
)

@api_view(['POST'])
def ingest_sensor_data(request):
    """
    Endpoint for ESP32 to send sensor data
    POST /api/iot/ingest/
    """
    # Verify API key
    api_key = request.headers.get('X-API-Key')
    expected_key = 'hackathon-2025-secure-key'  # Should match .env
    
    if api_key != expected_key:
        return Response(
            {'error': 'Invalid API key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Validate and save data
    serializer = SensorDataIngestSerializer(data=request.data)
    
    if serializer.is_valid():
        sensor_data = serializer.save()
        return Response({
            'status': 'success',
            'message': 'Data received',
            'data_id': str(sensor_data.id)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceViewSet(viewsets.ModelViewSet):
    """API endpoints for Device management"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign device to an animal
        POST /api/iot/devices/{id}/assign/
        Body: {"animal_id": "uuid"}
        """
        device = self.get_object()
        animal_id = request.data.get('animal_id')
        
        if not animal_id:
            return Response(
                {'error': 'animal_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.core.models import Animal
        try:
            animal = Animal.objects.get(id=animal_id)
            device.animal = animal
            device.save()
            return Response({
                'message': f'Device {device.device_id} assigned to {animal.tag_id}'
            })
        except Animal.DoesNotExist:
            return Response(
                {'error': 'Animal not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SensorDataViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for viewing sensor data"""
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by animal
        animal_id = self.request.query_params.get('animal_id')
        if animal_id:
            queryset = queryset.filter(animal__id=animal_id)
        
        # Filter by device
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Filter by time range (default: last 24 hours)
        hours = int(self.request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset