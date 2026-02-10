from django import forms
from .models import Device
from apps.core.models import Animal


class DeviceRegistrationForm(forms.ModelForm):
    """Form for registering a new IoT device"""
    
    class Meta:
        model = Device
        fields = ['device_id', 'animal', 'firmware_version', 'status']
        widgets = {
            'device_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter device ID (e.g., ESP32-001)',
                'required': True
            }),
            'animal': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select animal (optional)'
            }),
            'firmware_version': forms.TextInput(attrs={
                'class': 'form-control',
                'value': '1.0.0'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].required = False
        self.fields['animal'].queryset = Animal.objects.all().order_by('tag_id')
