from django.contrib import admin
from .models import Device, SensorData

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'animal', 'status', 'battery_level', 'last_seen']
    list_filter = ['status']
    search_fields = ['device_id', 'animal__tag_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['device', 'animal', 'timestamp', 'body_temperature', 'battery_level']
    list_filter = ['timestamp']
    search_fields = ['device__device_id', 'animal__tag_id']
    readonly_fields = ['created_at', 'activity_level']
    date_hierarchy = 'timestamp'