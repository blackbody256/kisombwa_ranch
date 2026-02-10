from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Avg, Count, Q, F, Max
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import datetime, timedelta
from apps.livestock.models import Animal, WeightRecord, HealthRecord, Vaccination
from decimal import Decimal
import csv

def analytics_dashboard(request):
    """Analytics dashboard with charts and statistics"""
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    # Total herd statistics
    total_animals = Animal.objects.filter(status='ACTIVE').count()
    
    # Weight analytics
    recent_weights = WeightRecord.objects.select_related('animal').order_by('-date')[:10]
    avg_weight = WeightRecord.objects.aggregate(Avg('weight'))['weight__avg'] or 0
    
    # Calculate average daily weight gain
    weight_records = WeightRecord.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('animal', 'date')
    
    # Group by animal and calculate weight gain
    weight_gain_data = []
    for animal in Animal.objects.filter(status='ACTIVE'):
        animal_weights = weight_records.filter(animal=animal).order_by('date')
        if animal_weights.count() >= 2:
            first_weight = animal_weights.first()
            last_weight = animal_weights.last()
            days_diff = (last_weight.date - first_weight.date).days
            if days_diff > 0:
                daily_gain = (last_weight.weight - first_weight.weight) / days_diff
                weight_gain_data.append(daily_gain)
    
    avg_weight_gain = sum(weight_gain_data) / len(weight_gain_data) if weight_gain_data else 0
    
    # Weight trends by date (last 30 days)
    weight_trends = WeightRecord.objects.filter(
        date__gte=thirty_days_ago
    ).values('date').annotate(
        avg_weight=Avg('weight')
    ).order_by('date')
    
    # Health analytics
    total_health_records = HealthRecord.objects.filter(date__gte=thirty_days_ago).count()
    critical_cases = HealthRecord.objects.filter(
        date__gte=thirty_days_ago,
        severity__in=['HIGH', 'CRITICAL']
    ).count()
    
    # Mortality rate calculation
    total_animals_ever = Animal.objects.count()
    deceased_animals = Animal.objects.filter(status='DECEASED').count()
    mortality_rate = (deceased_animals / total_animals_ever * 100) if total_animals_ever > 0 else 0
    
    # Breed distribution
    breed_distribution = Animal.objects.filter(status='ACTIVE').values('breed').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Add colors for breed visualization
    colors = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    breed_data = []
    for i, breed in enumerate(breed_distribution):
        breed_data.append({
            'name': breed['breed'],
            'count': breed['count'],
            'color': colors[i % len(colors)]
        })
    
    # Vaccination statistics
    total_vaccinations = Vaccination.objects.filter(
        date_administered__gte=thirty_days_ago
    ).count()
    
    vaccinations_due = Vaccination.objects.filter(
        next_due_date__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    
    # Health costs (last 30 days)
    health_costs = HealthRecord.objects.filter(
        date__gte=thirty_days_ago
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    vaccination_costs = Vaccination.objects.filter(
        date_administered__gte=thirty_days_ago
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    total_health_expenses = health_costs + vaccination_costs
    
    # Gender distribution
    gender_stats = Animal.objects.filter(status='ACTIVE').values('gender').annotate(
        count=Count('id')
    )
    
    # Status distribution (actual data from animals)
    status_distribution = []
    total_animals_for_status = Animal.objects.filter(status='ACTIVE').count()
    if total_animals_for_status > 0:
        status_data = Animal.objects.values('status').annotate(count=Count('id'))
        colors = {'ACTIVE': '#22c55e', 'QUARANTINE': '#f59e0b', 'SOLD': '#3b82f6', 'DECEASED': '#ef4444'}
        for status in status_data:
            percentage = (status['count'] / Animal.objects.count() * 100)
            status_distribution.append({
                'name': status['status'].replace('_', ' ').title(),
                'percentage': round(percentage, 1),
                'count': status['count'],
                'color': colors.get(status['status'], '#8b5cf6')
            })
    
    # Estimated herd value (simplified calculation based on average weight)
    avg_price_per_kg = 5  # USD per kg (can be configurable)
    total_weight = WeightRecord.objects.filter(
        animal__status='ACTIVE',
        date__gte=thirty_days_ago
    ).values('animal').annotate(
        latest_weight=Max('weight')
    ).aggregate(total=Sum('latest_weight'))['total'] or 0
    
    herd_value = float(total_weight) * avg_price_per_kg / 1000000  # Convert to millions
    
    context = {
        'total_animals': total_animals,
        'recent_weights': recent_weights,
        'avg_weight': round(avg_weight, 2),
        'avg_weight_gain': round(avg_weight_gain, 2),
        'weight_trends': list(weight_trends),
        'total_health_records': total_health_records,
        'critical_cases': critical_cases,
        'mortality_rate': round(mortality_rate, 1),
        'breed_distribution': breed_data,
        'total_vaccinations': total_vaccinations,
        'vaccinations_due': vaccinations_due,
        'total_health_expenses': float(total_health_expenses),
        'gender_stats': gender_stats,
        'status_distribution': status_distribution,
        'herd_value': round(herd_value, 1),
        'weight_gain_trend': None,  # Can be calculated with historical comparison
        'mortality_trend': None,  # Can be calculated with historical comparison
        'feed_efficiency': 6.5,  # Placeholder - needs feed data
        'feed_efficiency_trend': None,
        'herd_value_growth': None,  # Can be calculated with historical comparison
    }
    return render(request, 'analytics/dashboard.html', context)


def export_report(request):
    """Export analytics report as CSV"""
    # Get date range from request parameters
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="kisombwa_ranch_analytics_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Kisombwa Ranch - Analytics Report'])
    writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([f'Period: Last {days} days ({date_from} to {timezone.now().date()})'])
    writer.writerow([])
    
    # Overall Statistics
    writer.writerow(['OVERALL STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    
    total_animals = Animal.objects.filter(status='ACTIVE').count()
    total_animals_all = Animal.objects.count()
    deceased_animals = Animal.objects.filter(status='DECEASED').count()
    mortality_rate = (deceased_animals / total_animals_all * 100) if total_animals_all > 0 else 0
    
    writer.writerow(['Active Animals', total_animals])
    writer.writerow(['Total Animals (All Time)', total_animals_all])
    writer.writerow(['Deceased Animals', deceased_animals])
    writer.writerow(['Mortality Rate (%)', f'{mortality_rate:.1f}'])
    writer.writerow([])
    
    # Weight Analytics
    writer.writerow(['WEIGHT ANALYTICS'])
    writer.writerow(['Metric', 'Value'])
    
    avg_weight = WeightRecord.objects.aggregate(Avg('weight'))['weight__avg'] or 0
    writer.writerow(['Average Weight (kg)', f'{avg_weight:.2f}'])
    
    # Calculate weight gain
    weight_records = WeightRecord.objects.filter(date__gte=date_from).order_by('animal', 'date')
    weight_gain_data = []
    for animal in Animal.objects.filter(status='ACTIVE'):
        animal_weights = weight_records.filter(animal=animal).order_by('date')
        if animal_weights.count() >= 2:
            first_weight = animal_weights.first()
            last_weight = animal_weights.last()
            days_diff = (last_weight.date - first_weight.date).days
            if days_diff > 0:
                daily_gain = (last_weight.weight - first_weight.weight) / days_diff
                weight_gain_data.append(daily_gain)
    
    avg_weight_gain = sum(weight_gain_data) / len(weight_gain_data) if weight_gain_data else 0
    writer.writerow(['Average Daily Weight Gain (kg)', f'{avg_weight_gain:.2f}'])
    writer.writerow([])
    
    # Health Analytics
    writer.writerow(['HEALTH ANALYTICS'])
    writer.writerow(['Metric', 'Value'])
    
    total_health_records = HealthRecord.objects.filter(date__gte=date_from).count()
    critical_cases = HealthRecord.objects.filter(
        date__gte=date_from,
        severity__in=['HIGH', 'CRITICAL']
    ).count()
    
    writer.writerow(['Total Health Records', total_health_records])
    writer.writerow(['Critical Cases', critical_cases])
    writer.writerow([])
    
    # Vaccination Statistics
    writer.writerow(['VACCINATION STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    
    total_vaccinations = Vaccination.objects.filter(date_administered__gte=date_from).count()
    vaccinations_due = Vaccination.objects.filter(
        next_due_date__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    
    writer.writerow(['Vaccinations Administered', total_vaccinations])
    writer.writerow(['Vaccinations Due (Next 7 Days)', vaccinations_due])
    writer.writerow([])
    
    # Financial Summary
    writer.writerow(['FINANCIAL SUMMARY'])
    writer.writerow(['Category', 'Amount (UGX)'])
    
    health_costs = HealthRecord.objects.filter(date__gte=date_from).aggregate(total=Sum('cost'))['total'] or 0
    vaccination_costs = Vaccination.objects.filter(date_administered__gte=date_from).aggregate(total=Sum('cost'))['total'] or 0
    total_expenses = health_costs + vaccination_costs
    
    writer.writerow(['Health Treatment Costs', f'{health_costs:,.2f}'])
    writer.writerow(['Vaccination Costs', f'{vaccination_costs:,.2f}'])
    writer.writerow(['Total Health Expenses', f'{total_expenses:,.2f}'])
    writer.writerow([])
    
    # Breed Distribution
    writer.writerow(['BREED DISTRIBUTION'])
    writer.writerow(['Breed', 'Count', 'Percentage'])
    
    breed_distribution = Animal.objects.filter(status='ACTIVE').values('breed').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for breed in breed_distribution:
        percentage = (breed['count'] / total_animals * 100) if total_animals > 0 else 0
        writer.writerow([breed['breed'], breed['count'], f'{percentage:.1f}%'])
    
    writer.writerow([])
    
    # Gender Distribution
    writer.writerow(['GENDER DISTRIBUTION'])
    writer.writerow(['Gender', 'Count', 'Percentage'])
    
    gender_stats = Animal.objects.filter(status='ACTIVE').values('gender').annotate(count=Count('id'))
    for gender in gender_stats:
        percentage = (gender['count'] / total_animals * 100) if total_animals > 0 else 0
        gender_name = 'Male' if gender['gender'] == 'M' else 'Female' if gender['gender'] == 'F' else 'Unknown'
        writer.writerow([gender_name, gender['count'], f'{percentage:.1f}%'])
    
    writer.writerow([])
    
    # Recent Weight Records
    writer.writerow(['RECENT WEIGHT RECORDS (Last 20)'])
    writer.writerow(['Date', 'Animal Tag', 'Weight (kg)', 'Notes'])
    
    recent_weights = WeightRecord.objects.select_related('animal').order_by('-date')[:20]
    for weight in recent_weights:
        writer.writerow([
            weight.date,
            weight.animal.tag_id,
            f'{weight.weight:.2f}',
            weight.notes or ''
        ])
    
    writer.writerow([])
    
    # Recent Health Records
    writer.writerow(['RECENT HEALTH RECORDS (Last 20)'])
    writer.writerow(['Date', 'Animal Tag', 'Diagnosis', 'Severity', 'Treatment', 'Cost (UGX)'])
    
    recent_health = HealthRecord.objects.select_related('animal').order_by('-date')[:20]
    for health in recent_health:
        writer.writerow([
            health.date,
            health.animal.tag_id,
            health.diagnosis,
            health.severity,
            health.treatment,
            f'{health.cost:,.2f}' if health.cost else '0.00'
        ])
    
    return response
