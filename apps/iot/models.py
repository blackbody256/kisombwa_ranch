import uuid
from django.db import models
from apps.core.models import Animal

# Create your models here.
class Device(models.Model):
    """Iot collar device"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=50, unique=True, db_index=True)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    firmware_version = models.CharField(max_length=20, default='1.0.0')
    battery_level = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'devices'
    
    def __str__(self):
        return f"{self.device_id} ({self.status})"
    
class SensorData(models.Model):
    """Raw sensor readings from collar"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_readings')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='sensor_data', null=True, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(db_index=True)
    
    # GPS data
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    satellites = models.IntegerField(default=0)
    
    # Temperature data
    body_temperature = models.FloatField()
    ambient_temperature = models.FloatField()
    
    # Accelerometer data
    acc_x = models.FloatField()
    acc_y = models.FloatField()
    acc_z = models.FloatField()
    activity_level = models.FloatField(null=True, blank=True)  # Calculated from accelerometer
    
    # Metadata
    battery_level = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sensor_data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['animal', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.device_id} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Calculate activity level from accelerometer magnitude
        if self.acc_x is not None and self.acc_y is not None and self.acc_z is not None:
            import math
            self.activity_level = math.sqrt(self.acc_x**2 + self.acc_y**2 + self.acc_z**2)
        super().save(*args, **kwargs)
    
