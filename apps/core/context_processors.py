"""
Context processors for global template variables
"""
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta


def global_context(request):
    """
    Add global context variables available in all templates
    """
    context = {}
    
    # User information
    if request.user.is_authenticated:
        # Get full name or username
        full_name = request.user.get_full_name() or request.user.username
        # Get first name for greeting
        first_name = request.user.first_name or request.user.username
        context['user_full_name'] = full_name
        context['user_first_name'] = first_name
        context['user_role'] = 'Ranch Manager'  # Can be expanded with actual roles
        context['user_email'] = request.user.email
    else:
        context['user_full_name'] = 'Guest'
        context['user_first_name'] = 'Guest'
        context['user_role'] = 'Visitor'
        context['user_email'] = ''
    
    # Notification count from alerts
    from apps.alerts.models import Alert
    unread_notifications = Alert.objects.filter(is_read=False).count()
    context['unread_notifications'] = unread_notifications
    
    # Ranch information from settings
    from apps.core.models import SystemSetting
    
    # Get ranch settings
    ranch_name_setting = SystemSetting.objects.filter(setting_key='ranch_name').first()
    ranch_location_setting = SystemSetting.objects.filter(setting_key='ranch_location').first()
    ranch_size_setting = SystemSetting.objects.filter(setting_key='ranch_size_hectares').first()
    
    context['ranch_name'] = ranch_name_setting.get_value() if ranch_name_setting else 'Kisombwa Ranch'
    context['ranch_location'] = ranch_location_setting.get_value() if ranch_location_setting else 'Mubende District, Uganda'
    context['ranch_size_hectares'] = ranch_size_setting.get_value() if ranch_size_setting else 2400
    
    # Weather data from IoT sensors
    from apps.iot.models import SensorData
    
    recent_weather_data = SensorData.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1),
        ambient_temperature__isnull=False
    ).order_by('-timestamp').first()
    
    if recent_weather_data:
        weather_temp = round(recent_weather_data.ambient_temperature, 0)
        # Simple weather condition based on temperature
        if weather_temp > 30:
            weather_condition = "Hot & Sunny"
        elif weather_temp > 25:
            weather_condition = "Partly Cloudy"
        elif weather_temp > 20:
            weather_condition = "Cloudy"
        else:
            weather_condition = "Cool"
        
        # Humidity estimate based on temperature
        if weather_temp > 28:
            weather_humidity = 60
        else:
            weather_humidity = 70
    else:
        # Default values if no sensor data
        weather_temp = 28
        weather_condition = "Partly Cloudy"
        weather_humidity = 65
    
    context['weather_temp'] = weather_temp
    context['weather_condition'] = weather_condition
    context['weather_humidity'] = weather_humidity
    
    return context
