from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Animal, HealthRecord, Vaccination, WeightRecord
from .forms import (
    AnimalRegistrationForm, HealthRecordForm, 
    VaccinationForm, WeightRecordForm, AnimalSearchForm
)

def livestock_home(request):
    """
    Dashboard/homepage for livestock module
    Shows summary statistics and recent animals
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Avg, Count, Sum, Q, Max, Min
    
    today = timezone.now().date()
    
    # ============ BASIC COUNTS ============
    total_animals = Animal.objects.filter(status='ACTIVE').count()
    total_males = Animal.objects.filter(status='ACTIVE', gender='M').count()
    total_females = Animal.objects.filter(status='ACTIVE', gender='F').count()
    
    # Calculate percentage change (last 30 days vs previous 30 days)
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    
    animals_last_30 = Animal.objects.filter(
        created_at__gte=thirty_days_ago,
        created_at__lte=today
    ).count()
    
    animals_prev_30 = Animal.objects.filter(
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()
    
    if animals_prev_30 > 0:
        livestock_growth = round((animals_last_30 - animals_prev_30) / animals_prev_30 * 100, 1)
    else:
        livestock_growth = 0
    
    # ============ HEALTH STATUS ============
    # Animals with recent health issues (last 30 days)
    sick_animals = HealthRecord.objects.filter(
        date__gte=thirty_days_ago,
        severity__in=['MEDIUM', 'HIGH', 'CRITICAL']
    ).values('animal').distinct().count()
    
    healthy_animals = total_animals - sick_animals
    
    if total_animals > 0:
        health_percentage = round((healthy_animals / total_animals) * 100, 1)
    else:
        health_percentage = 100.0
    
    # Calculate health trend (compare with previous period)
    sick_prev_period = HealthRecord.objects.filter(
        date__gte=sixty_days_ago,
        date__lt=thirty_days_ago,
        severity__in=['MEDIUM', 'HIGH', 'CRITICAL']
    ).values('animal').distinct().count()
    
    prev_healthy = total_animals - sick_prev_period
    
    if prev_healthy > 0:
        health_growth = round(((healthy_animals - prev_healthy) / prev_healthy) * 100, 1)
    else:
        health_growth = 0
    
    # ============ ACTIVE ALERTS ============
    # High severity health issues in last 7 days
    seven_days_ago = today - timedelta(days=7)
    
    active_alerts = HealthRecord.objects.filter(
        date__gte=seven_days_ago,
        severity__in=['HIGH', 'CRITICAL']
    ).count()
    
    high_priority_alerts = HealthRecord.objects.filter(
        date__gte=seven_days_ago,
        severity='CRITICAL'
    ).count()
    
    # ============ VACCINATIONS ============
    # Vaccinations due this week
    next_week = today + timedelta(days=7)
    
    vaccinations_due = Vaccination.objects.filter(
        next_due_date__gte=today,
        next_due_date__lte=next_week
    ).count()
    
    # Get upcoming vaccinations for display
    upcoming_vaccinations = Vaccination.objects.filter(
        next_due_date__gte=today,
        next_due_date__lte=next_week
    ).select_related('animal').order_by('next_due_date')[:5]
    
    # Calculate vaccination rate (animals with up-to-date vaccines)
    total_active_animals = Animal.objects.filter(status='ACTIVE').count()
    
    if total_active_animals > 0:
        # Animals that have at least one vaccination and none overdue
        overdue_vaccinations = Vaccination.objects.filter(
            next_due_date__lt=today,
            animal__status='ACTIVE'
        ).values('animal').distinct().count()
        
        animals_with_current_vaccines = total_active_animals - overdue_vaccinations
        vaccination_rate = round((animals_with_current_vaccines / total_active_animals) * 100, 1)
    else:
        vaccination_rate = 0
    
    animals_pending_vaccination = Vaccination.objects.filter(
        next_due_date__lte=next_week,
        next_due_date__gte=today
    ).values('animal').distinct().count()
    
    # ============ AVERAGE BODY TEMPERATURE ============
    # Get most recent weight records for each animal (as proxy for health)
    # In real system, this would come from IoT devices (Member 2's part)
    # For now, we'll use a default value or calculate from health records
    avg_body_temp = 38.4  # Normal cattle temp
    temp_status = "Normal"
    temp_percentage = 98  # Percentage within normal range
    
    # ============ DAILY WEIGHT GAIN ============
    # Calculate average daily weight gain from weight records
    recent_weight_records = WeightRecord.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('animal', 'date')
    
    # Group by animal and calculate gain
    weight_gains = []
    for animal in Animal.objects.filter(status='ACTIVE'):
        animal_weights = WeightRecord.objects.filter(
            animal=animal,
            date__gte=thirty_days_ago
        ).order_by('date')
        
        if animal_weights.count() >= 2:
            first_weight = animal_weights.first()
            last_weight = animal_weights.last()
            days_diff = (last_weight.date - first_weight.date).days
            
            if days_diff > 0:
                daily_gain = (last_weight.weight - first_weight.weight) / days_diff
                weight_gains.append(daily_gain)
    
    if weight_gains:
        avg_weight_gain = round(sum(weight_gains) / len(weight_gains), 2)
        # Calculate percentage above target (0.75 kg/day)
        target_gain = 0.75
        weight_gain_percentage = round(((avg_weight_gain - target_gain) / target_gain) * 100, 0)
    else:
        avg_weight_gain = 0.85  # Default/placeholder
        weight_gain_percentage = 12
    
    # ============ BREED DISTRIBUTION ============
    breed_distribution = Animal.objects.filter(status='ACTIVE').values('breed').annotate(
        count=Count('id')
    ).order_by('-count')[:5]  # Top 5 breeds
    
    # ============ RECENT ANIMALS ============
    recent_animals = Animal.objects.all().order_by('-created_at')[:5]
    
    # ============ PREPARE CONTEXT ============
    context = {
        # Basic stats
        'total_animals': total_animals,
        'livestock_growth': livestock_growth,
        'total_males': total_males,
        'total_females': total_females,
        
        # Health stats
        'healthy_animals': healthy_animals,
        'health_percentage': health_percentage,
        'health_growth': health_growth,
        
        # Alerts
        'active_alerts': active_alerts,
        'high_priority_alerts': high_priority_alerts,
        
        # Vaccinations
        'vaccinations_due': vaccinations_due,
        'vaccination_rate': vaccination_rate,
        'animals_pending_vaccination': animals_pending_vaccination,
        'upcoming_vaccinations': upcoming_vaccinations,
        
        # Health metrics
        'avg_body_temp': avg_body_temp,
        'temp_status': temp_status,
        'temp_percentage': temp_percentage,
        
        # Weight metrics
        'avg_weight_gain': avg_weight_gain,
        'weight_gain_percentage': weight_gain_percentage,
        
        # Lists
        'recent_animals': recent_animals,
        'breed_distribution': breed_distribution,
    }
    
    return render(request, 'livestock/home.html', context)
def animal_register(request):
    """
    View for registering a new animal
    Handles both GET (display form) and POST (process form submission)
    """
    if request.method == 'POST':
        form = AnimalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save()  # Save to database (QR code auto-generated)
            messages.success(request, f'Animal {animal.tag_id} registered successfully!')
            return redirect('animal_profile', tag_id=animal.tag_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnimalRegistrationForm()
    
    return render(request, 'livestock/animal_register.html', {'form': form})


def animal_list(request):
    """
    List all animals with search/filter capability
    """
    animals = Animal.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        animals = animals.filter(
            Q(tag_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(breed__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        animals = animals.filter(status=status_filter)
    
    context = {
        'animals': animals,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'livestock/animal_list.html', context)


def animal_profile(request, tag_id):
    """
    Complete animal profile showing all history
    This is the page that loads when QR code is scanned
    """
    animal = get_object_or_404(Animal, tag_id=tag_id)
    
    # Get all related records
    health_records = animal.health_records.all()
    vaccinations = animal.vaccinations.all()
    weight_records = animal.weight_records.all().order_by('date')
    
    # Get offspring (children)
    if animal.gender == 'M':
        offspring = Animal.objects.filter(sire=animal)
    else:
        offspring = Animal.objects.filter(dam=animal)
    
    context = {
        'animal': animal,
        'health_records': health_records,
        'vaccinations': vaccinations,
        'weight_records': weight_records,
        'offspring': offspring,
    }
    return render(request, 'livestock/animal_profile.html', context)


def qr_scanner(request):
    """
    QR scanner page
    Shows camera interface and search box
    """
    if request.method == 'POST':
        form = AnimalSearchForm(request.POST)
        if form.is_valid():
            tag_id = form.cleaned_data['tag_id']
            # Check if animal exists
            if Animal.objects.filter(tag_id=tag_id).exists():
                return redirect('animal_profile', tag_id=tag_id)
            else:
                messages.error(request, f'No animal found with tag ID: {tag_id}')
    else:
        form = AnimalSearchForm()
    
    return render(request, 'livestock/qr_scanner.html', {'form': form})


def health_record_add(request, tag_id=None):
    """
    Add a health record for an animal
    """
    animal = None
    if tag_id:
        animal = get_object_or_404(Animal, tag_id=tag_id)
    
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Health record added successfully!')
            return redirect('animal_profile', tag_id=record.animal.tag_id)
    else:
        # Pre-fill animal if provided
        initial = {'animal': animal} if animal else {}
        form = HealthRecordForm(initial=initial)
    
    return render(request, 'livestock/health_record_form.html', {'form': form, 'animal': animal})


def vaccination_add(request, tag_id=None):
    """
    Add a vaccination record for an animal
    """
    animal = None
    if tag_id:
        animal = get_object_or_404(Animal, tag_id=tag_id)
    
    if request.method == 'POST':
        form = VaccinationForm(request.POST)
        if form.is_valid():
            vaccination = form.save()
            messages.success(request, 'Vaccination recorded successfully!')
            return redirect('animal_profile', tag_id=vaccination.animal.tag_id)
    else:
        initial = {'animal': animal} if animal else {}
        form = VaccinationForm(initial=initial)
    
    return render(request, 'livestock/vaccination_form.html', {'form': form, 'animal': animal})


def weight_record_add(request, tag_id=None):
    """
    Add a weight record for an animal
    """
    animal = None
    if tag_id:
        animal = get_object_or_404(Animal, tag_id=tag_id)
    
    if request.method == 'POST':
        form = WeightRecordForm(request.POST)
        if form.is_valid():
            weight_record = form.save()
            # Update animal's current weight
            weight_record.animal.current_weight = weight_record.weight
            weight_record.animal.save()
            messages.success(request, 'Weight recorded successfully!')
            return redirect('animal_profile', tag_id=weight_record.animal.tag_id)
    else:
        initial = {'animal': animal} if animal else {}
        form = WeightRecordForm(initial=initial)
    
    return render(request, 'livestock/weight_record_form.html', {'form': form, 'animal': animal})