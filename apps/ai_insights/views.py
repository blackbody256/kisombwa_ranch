from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import MLModel, Prediction
from apps.livestock.models import Animal, HealthRecord
from apps.iot.models import SensorData


def ai_insights_dashboard(request):
    """AI Insights dashboard with predictions and recommendations"""
    
    # Get active ML models
    active_models_queryset = MLModel.objects.all().order_by('-is_active', '-accuracy')
    
    # Manually add prediction counts to each model
    for model in active_models_queryset:
        model.prediction_count = Prediction.objects.filter(
            model_name=model.name,
            model_version=model.version
        ).count()
    
    active_models_count = active_models_queryset.filter(is_active=True).count()
    
    # Get recent predictions (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_predictions = Prediction.objects.filter(
        predicted_at__gte=seven_days_ago
    )
    
    total_predictions = recent_predictions.count()
    
    # Calculate average confidence/accuracy
    avg_confidence = recent_predictions.aggregate(
        avg=Avg('confidence_score')
    )['avg'] or 0
    accuracy_rate = avg_confidence * 100  # Convert to percentage
    
    # High-risk predictions (health issues, anomalies with high confidence)
    high_risk_predictions = recent_predictions.filter(
        Q(prediction_type__in=['health', 'anomaly']),
        confidence_score__gte=0.75,
        predicted_value__in=['SICK', 'CRITICAL', 'ANOMALY', 'HIGH_RISK']
    ).select_related('animal').order_by('-predicted_at')[:10]
    
    # Prediction type breakdown
    prediction_breakdown = recent_predictions.values('prediction_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Animals with recent predictions
    animals_with_predictions = recent_predictions.values('animal').distinct().count()
    
    # Estrus cycle predictions
    estrus_predictions = recent_predictions.filter(
        prediction_type='estrus',
        confidence_score__gte=0.70
    ).select_related('animal').order_by('-predicted_at')[:5]
    
    # Behavior insights
    behavior_predictions = recent_predictions.filter(
        prediction_type='behavior'
    ).values('predicted_value').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Calculate alerts prevented from predictions vs actual health records
    # Count high-confidence health predictions that preceded actual health records
    alerts_prevented = 0
    for prediction in recent_predictions.filter(
        prediction_type='health',
        confidence_score__gte=0.80
    ):
        # Check if there's a health record within 48 hours after prediction
        subsequent_records = HealthRecord.objects.filter(
            animal=prediction.animal,
            date__gte=prediction.predicted_at.date(),
            date__lte=prediction.predicted_at.date() + timedelta(days=2)
        ).count()
        if subsequent_records > 0:
            alerts_prevented += 1
    
    # Calculate data points per day from IoT sensors
    try:
        sensor_readings_today = SensorData.objects.filter(
            timestamp__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        data_points_per_day = sensor_readings_today or 0
    except:
        data_points_per_day = 0
    
    # Recent prediction trends
    prediction_trends = []
    for i in range(7):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        count = Prediction.objects.filter(
            predicted_at__gte=day_start,
            predicted_at__lte=day_end
        ).count()
        prediction_trends.append({
            'date': day.strftime('%b %d'),
            'count': count
        })
    prediction_trends.reverse()
    
    context = {
        'active_models': active_models_queryset,
        'active_models_count': active_models_count,
        'total_predictions': total_predictions,
        'accuracy_rate': round(accuracy_rate, 1) if accuracy_rate > 0 else 0,
        'alerts_prevented': alerts_prevented,
        'data_points_per_day': data_points_per_day,
        'high_risk_predictions': high_risk_predictions,
        'prediction_breakdown': prediction_breakdown,
        'animals_with_predictions': animals_with_predictions,
        'estrus_predictions': estrus_predictions,
        'behavior_predictions': behavior_predictions,
        'prediction_trends': prediction_trends,
    }
    
    return render(request, 'ai_insights/dashboard.html', context)
