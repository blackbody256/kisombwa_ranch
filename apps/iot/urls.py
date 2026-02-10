from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'sensor-data', views.SensorDataViewSet)

app_name = 'iot'

urlpatterns = [
    path('', views.iot_dashboard, name='dashboard'),
    path('register/', views.register_device, name='register_device'),
    path('sync-all/', views.sync_all_devices, name='sync_all'),
    path('device/<uuid:device_id>/', views.device_detail, name='device_detail'),
    path('ingest/', views.ingest_sensor_data, name='iot-ingest'),
    path('api/', include(router.urls)),
]