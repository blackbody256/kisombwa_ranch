from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import Device, SensorData

class SensorDataIngestSerializer(serializers.Serializer):
    """Serializer for incoming sensor data from ESP32"""
    device_id = serializers.CharField(max_length=50)
    timestamp = serializers.CharField()  # Will convert to datetime
    
    # Nested objects
    gps = serializers.DictField()
    temperature = serializers.DictField()
    accelerometer = serializers.DictField()
    battery = serializers.IntegerField()
    
    def validate_device_id(self, value):
        """Check if device exists"""
        try:
            Device.objects.get(device_id=value)
        except Device.DoesNotExist:
            raise serializers.ValidationError(f"Device {value} not found")
        return value
    
    def create(self, validated_data):
        """Create SensorData record"""
        device = Device.objects.get(device_id=validated_data['device_id'])
        
        # Parse timestamp (convert millis to datetime for demo)
        try:
            timestamp_ms = int(validated_data['timestamp'])
            timestamp = timezone.make_aware(datetime.fromtimestamp(timestamp_ms / 1000.0))
        except:
            timestamp = timezone.now()
        
        # Extract nested data
        gps_data = validated_data['gps']
        temp_data = validated_data['temperature']
        accel_data = validated_data['accelerometer']
        
        # Create sensor data record
        sensor_data = SensorData.objects.create(
            device=device,
            animal=device.animal,
            timestamp=timestamp,
            latitude=gps_data['latitude'],
            longitude=gps_data['longitude'],
            altitude=gps_data.get('altitude', 0),
            satellites=gps_data.get('satellites', 0),
            body_temperature=temp_data['body'],
            ambient_temperature=temp_data['ambient'],
            acc_x=accel_data['x'],
            acc_y=accel_data['y'],
            acc_z=accel_data['z'],
            battery_level=validated_data['battery']
        )
        
        # Update device last seen and battery
        device.last_seen = timestamp
        device.battery_level = validated_data['battery']
        device.save()
        
        return sensor_data

class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer for displaying sensor data"""
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    
    class Meta:
        model = SensorData
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    animal_tag = serializers.CharField(source='animal.tag_id', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'