from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Alert
from apps.livestock.models import Animal, HealthRecord, Vaccination
from apps.iot.models import Device, SensorData
from apps.ai_insights.models import Prediction


def alerts_dashboard(request):
    """Main alerts dashboard showing all alerts"""
    
    # Get filter parameters
    severity_filter = request.GET.get('severity', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', 'active')  # active, resolved, all
    
    # Base queryset
    alerts = Alert.objects.select_related('animal', 'resolved_by')
    
    # Apply filters
    if status_filter == 'active':
        alerts = alerts.filter(is_resolved=False)
    elif status_filter == 'resolved':
        alerts = alerts.filter(is_resolved=True)
    
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    if type_filter:
        alerts = alerts.filter(alert_type=type_filter)
    
    # Get statistics
    total_alerts = alerts.count()
    critical_alerts = alerts.filter(severity='critical').count()
    unread_alerts = alerts.filter(is_read=False).count()
    
    # Alerts by severity
    severity_breakdown = alerts.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    # Alerts by type
    type_breakdown = alerts.values('alert_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Recent alerts (last 24 hours)
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    recent_alerts_count = Alert.objects.filter(
        created_at__gte=twenty_four_hours_ago
    ).count()
    
    # Animals with most alerts
    animals_with_alerts = alerts.filter(
        animal__isnull=False
    ).values(
        'animal__tag_id', 'animal__name', 'animal__id'
    ).annotate(
        alert_count=Count('id')
    ).order_by('-alert_count')[:5]
    
    # Paginate alerts
    page_size = 20
    alerts_list = alerts[:page_size]
    
    context = {
        'alerts': alerts_list,
        'total_alerts': total_alerts,
        'critical_alerts': critical_alerts,
        'unread_alerts': unread_alerts,
        'recent_alerts_count': recent_alerts_count,
        'severity_breakdown': severity_breakdown,
        'type_breakdown': type_breakdown,
        'animals_with_alerts': animals_with_alerts,
        'severity_filter': severity_filter,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'alert_types': Alert.ALERT_TYPES,
        'severity_levels': Alert.SEVERITY_LEVELS,
    }
    
    return render(request, 'alerts/dashboard.html', context)


def mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.is_read = True
        alert.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


def resolve_alert(request, alert_id):
    """Mark an alert as resolved"""
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user if request.user.is_authenticated else None
        alert.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


def generate_alerts(request):
    """Generate alerts from various sources (can be called via cron/celery)"""
    alerts_created = 0
    
    # 1. Health-based alerts from livestock
    sick_animals = Animal.objects.filter(status='sick')
    for animal in sick_animals:
        # Check if alert already exists
        if not Alert.objects.filter(
            animal=animal,
            alert_type='health',
            is_resolved=False
        ).exists():
            Alert.objects.create(
                animal=animal,
                alert_type='health',
                severity='high',
                title=f'Health Issue: {animal.name or animal.tag_id}',
                message=f'Animal {animal.tag_id} is marked as sick and requires attention.',
                metadata={'source': 'livestock'}
            )
            alerts_created += 1
    
    # 2. Vaccination alerts
    today = timezone.now().date()
    upcoming_vaccinations = Vaccination.objects.filter(
        next_due_date__lte=today + timedelta(days=7),
        next_due_date__gte=today
    ).select_related('animal')
    
    for vaccination in upcoming_vaccinations:
        if not Alert.objects.filter(
            animal=vaccination.animal,
            alert_type='vaccination',
            is_resolved=False,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exists():
            days_until = (vaccination.next_due_date - today).days
            Alert.objects.create(
                animal=vaccination.animal,
                alert_type='vaccination',
                severity='medium',
                title=f'Vaccination Due: {vaccination.animal.tag_id}',
                message=f'Vaccination for {vaccination.vaccine_name} is due in {days_until} days.',
                metadata={
                    'source': 'livestock',
                    'vaccine_name': vaccination.vaccine_name,
                    'due_date': vaccination.next_due_date.isoformat()
                }
            )
            alerts_created += 1
    
    # 3. IoT device alerts (low battery, offline devices)
    low_battery_threshold = 20
    low_battery_devices = Device.objects.filter(
        battery_level__lt=low_battery_threshold,
        status='active'
    )
    
    for device in low_battery_devices:
        if not Alert.objects.filter(
            animal=device.animal,
            alert_type='battery',
            is_resolved=False,
            created_at__gte=timezone.now() - timedelta(hours=12)
        ).exists():
            Alert.objects.create(
                animal=device.animal,
                alert_type='battery',
                severity='medium' if device.battery_level > 10 else 'high',
                title=f'Low Battery: {device.device_id}',
                message=f'Device {device.device_id} battery at {device.battery_level}%.',
                metadata={
                    'source': 'iot',
                    'device_id': device.device_id,
                    'battery_level': device.battery_level
                }
            )
            alerts_created += 1
    
    # 4. Temperature alerts from sensor data
    one_hour_ago = timezone.now() - timedelta(hours=1)
    high_temp_threshold = 40.0  # degrees Celsius
    
    high_temp_readings = SensorData.objects.filter(
        timestamp__gte=one_hour_ago,
        body_temperature__gte=high_temp_threshold
    ).select_related('animal')
    
    for reading in high_temp_readings:
        if reading.animal and not Alert.objects.filter(
            animal=reading.animal,
            alert_type='temperature',
            is_resolved=False,
            created_at__gte=timezone.now() - timedelta(hours=6)
        ).exists():
            Alert.objects.create(
                animal=reading.animal,
                alert_type='temperature',
                severity='high',
                title=f'High Temperature: {reading.animal.tag_id}',
                message=f'Body temperature of {reading.body_temperature}°C detected.',
                metadata={
                    'source': 'iot',
                    'temperature': reading.body_temperature,
                    'reading_time': reading.timestamp.isoformat()
                }
            )
            alerts_created += 1
    
    # 5. AI prediction alerts (high-risk predictions)
    high_risk_predictions = Prediction.objects.filter(
        confidence_score__gte=0.80,
        prediction_type__in=['health', 'anomaly'],
        predicted_at__gte=timezone.now() - timedelta(hours=24)
    ).select_related('animal')
    
    for prediction in high_risk_predictions:
        if not Alert.objects.filter(
            animal=prediction.animal,
            alert_type='prediction',
            is_resolved=False,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists():
            Alert.objects.create(
                animal=prediction.animal,
                alert_type='prediction',
                severity='high' if prediction.confidence_score >= 0.90 else 'medium',
                title=f'AI Alert: {prediction.predicted_value}',
                message=f'AI model detected {prediction.prediction_type} issue with {prediction.confidence_score*100:.0f}% confidence.',
                metadata={
                    'source': 'ai_insights',
                    'model_name': prediction.model_name,
                    'confidence': prediction.confidence_score,
                    'prediction_type': prediction.prediction_type
                }
            )
            alerts_created += 1
    
    if request:
        return JsonResponse({
            'success': True,
            'alerts_created': alerts_created
        })
    
    return alerts_created
