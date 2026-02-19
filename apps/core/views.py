from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemSetting, Ranch, Animal
from apps.livestock.models import Animal as LivestockAnimal
from django.db.models import Count, Q

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')


def settings_view(request):
    """Settings page for system configuration"""
    if request.method == 'POST':
        # Process form submission
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                try:
                    setting = SystemSetting.objects.get(setting_key=setting_key)
                    
                    if setting.setting_type == 'boolean':
                        # Checkboxes are only present if checked
                        setting.is_enabled = True
                        setting.boolean_value = True
                    else:
                        setting.set_value(value)
                    
                    setting.save()
                except SystemSetting.DoesNotExist:
                    pass
        
        # Handle unchecked checkboxes (they won't be in POST data)
        all_boolean_settings = SystemSetting.objects.filter(setting_type='boolean')
        for setting in all_boolean_settings:
            key = f'setting_{setting.setting_key}'
            if key not in request.POST:
                setting.is_enabled = False
                setting.boolean_value = False
                setting.save()
        
        messages.success(request, 'Settings saved successfully!')
        return redirect('settings')
    
    # Get settings organized by category
    settings_by_category = {}
    for category_code, category_name in SystemSetting.CATEGORY_CHOICES:
        settings = SystemSetting.objects.filter(category=category_code)
        if settings.exists():
            settings_by_category[category_name] = settings
    
    # Get statistics for the dashboard section
    total_animals = LivestockAnimal.objects.count()
    active_animals = LivestockAnimal.objects.filter(status='ACTIVE').count()
    ranches = Ranch.objects.count()
    
    context = {
        'settings_by_category': settings_by_category,
        'total_animals': total_animals,
        'active_animals': active_animals,
        'ranches': ranches,
    }
    
    return render(request, 'settings.html', context)