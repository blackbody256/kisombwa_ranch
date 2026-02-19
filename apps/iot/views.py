from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, Avg
from datetime import timedelta
from .models import Device, SensorData
from .forms import DeviceRegistrationForm
from .serializers import (
    DeviceSerializer, 
    SensorDataSerializer, 
    SensorDataIngestSerializer
)


def iot_dashboard(request):
    """IoT Devices Dashboard"""
    # Get all devices
    devices = Device.objects.select_related('animal').all()
    
    # Calculate statistics
    total_devices = devices.count()
    active_devices = devices.filter(status='active').count()
    inactive_devices = devices.filter(status='inactive').count()
    low_battery = devices.filter(battery_level__lt=20).count()
    
    # Get devices with recent sensor data
    one_hour_ago = timezone.now() - timedelta(hours=1)
    devices_with_data = []
    
    for device in devices:
        # Get latest sensor reading
        latest_reading = device.sensor_readings.first()
        
        # Determine if device is online (has data in last hour)
        is_online = device.last_seen and device.last_seen >= one_hour_ago
        
        device_data = {
            'id': device.id,
            'device_id': device.device_id,
            'status': 'online' if is_online else 'offline',
            'battery_level': device.battery_level,
            'assigned_to': device.animal,
            'last_sync': device.last_seen,
            'signal_strength': None,
            'last_temperature': None,
            'activity_level': None,
        }
        
        if latest_reading:
            device_data['signal_strength'] = min(100, latest_reading.satellites * 20) if latest_reading.satellites else 0
            device_data['last_temperature'] = round(latest_reading.body_temperature, 1)
            device_data['activity_level'] = 'Active' if latest_reading.activity_level and latest_reading.activity_level > 1.0 else 'Resting'
        
        devices_with_data.append(device_data)
    
    # Calculate network health metrics
    recent_readings = SensorData.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    )
    
    # Device uptime (devices seen in last hour / total devices)
    devices_online = len([d for d in devices_with_data if d['status'] == 'online'])
    device_uptime = round((devices_online / total_devices * 100), 1) if total_devices > 0 else 0
    
    # Data sync rate (devices with recent data / total devices)
    data_sync_rate = round((recent_readings.values('device').distinct().count() / total_devices * 100), 1) if total_devices > 0 else 0
    
    # Signal quality (average signal strength)
    avg_satellites = recent_readings.aggregate(avg=Avg('satellites'))['avg'] or 0
    signal_quality = round(min(100, avg_satellites * 20), 1)
    
    # Get offline devices for alerts
    offline_devices = [d for d in devices_with_data if d['status'] == 'offline']
    
    context = {
        'devices': devices_with_data,
        'total_devices': total_devices,
        'active_devices': devices_online,
        'inactive_devices': total_devices - devices_online,
        'low_battery': low_battery,
        'device_uptime': device_uptime,
        'data_sync_rate': data_sync_rate,
        'signal_quality': signal_quality,
        'offline_devices': offline_devices[:5],  # Show top 5
    }
    
    return render(request, 'iot/dashboard.html', context)


def register_device(request):
    """Register a new IoT device"""
    if request.method == 'POST':
        form = DeviceRegistrationForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.battery_level = 100  # New devices start at 100%
            device.last_seen = timezone.now()
            device.save()
            messages.success(request, f'Device {device.device_id} registered successfully!')
            return redirect('iot:dashboard')
        else:
            messages.error(request, 'Error registering device. Please check the form.')
    else:
        form = DeviceRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'iot/register_device.html', context)


def sync_all_devices(request):
    """Trigger sync for all active devices"""
    if request.method == 'POST':
        active_devices = Device.objects.filter(status='active')
        count = active_devices.count()
        
        if count > 0:
            # Update last_seen timestamp for all active devices
            # In production, this would trigger actual device communication
            active_devices.update(last_seen=timezone.now())
            # Only show message if devices were actually synced
            messages.info(request, f'Synced {count} device(s) successfully')
        # Don't show message if no devices - let the UI handle it
        
        return redirect('iot:dashboard')
    
    return redirect('iot:dashboard')


def device_detail(request, device_id):
    """View and edit device details"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        form = DeviceRegistrationForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, f'Device {device.device_id} updated successfully!')
            return redirect('iot:dashboard')
    else:
        form = DeviceRegistrationForm(instance=device)
    
    # Get recent sensor readings
    recent_readings = device.sensor_readings.order_by('-timestamp')[:10]
    
    context = {
        'device': device,
        'form': form,
        'recent_readings': recent_readings,
    }
    return render(request, 'iot/device_detail.html', context)


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