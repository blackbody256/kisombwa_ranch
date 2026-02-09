from django import forms
from apps.core.models import Animal
from apps.iot.models import Device
from .models import HealthRecord, Vaccination, WeightRecord

class AnimalRegistrationForm(forms.ModelForm):
    """
    Form for registering a new animal
    Uses Django ModelForm to automatically generate fields from the Animal model
    """
    device = forms.ModelChoiceField(
        queryset=Device.objects.filter(animal__isnull=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select an available IoT collar device for this animal.',
    )

    class Meta:
        model = Animal
        fields = [
            'tag_id', 'name', 'breed', 'gender', 'birth_date',
            'color', 'weight_at_birth', 'sire', 'dam', 'photo'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tag_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., KSW-2024-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'breed': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Brown with white spots'}),
            'weight_at_birth': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kg'}),
            'sire': forms.Select(attrs={'class': 'form-control'}),
            'dam': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'tag_id': 'Must be unique. E.g., KSW-2024-001',
            'sire': 'Select the father (optional)',
            'dam': 'Select the mother (optional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter sire to show only males
        self.fields['sire'].queryset = Animal.objects.filter(gender='M')
        # Filter dam to show only females
        self.fields['dam'].queryset = Animal.objects.filter(gender='F')
        # Filter devices to show only those not yet assigned to an animal
        self.fields['device'].queryset = Device.objects.filter(animal__isnull=True)

    def save(self, commit=True):
        animal = super().save(commit=commit)
        device = self.cleaned_data.get('device')
        if device is not None:
            device.animal = animal
            if commit:
                device.save()
        return animal


class HealthRecordForm(forms.ModelForm):
    """
    Form for adding health records
    """
    class Meta:
        model = HealthRecord
        fields = [
            'animal', 'date', 'diagnosis', 'symptoms', 'treatment',
            'severity', 'cost', 'follow_up_date', 'recorded_by', 'notes'
        ]
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Foot and Mouth Disease'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe symptoms observed'}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Treatment given'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'UGX'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'recorded_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vet name'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VaccinationForm(forms.ModelForm):
    """
    Form for recording vaccinations
    """
    class Meta:
        model = Vaccination
        fields = [
            'animal', 'vaccine_name', 'disease', 'date_administered',
            'next_due_date', 'batch_number', 'administered_by',
            'dosage', 'route', 'cost', 'notes'
        ]
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'vaccine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., FMD Vaccine'}),
            'disease': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Foot and Mouth Disease'}),
            'date_administered': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'administered_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vet name'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2ml'}),
            'route': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., IM (Intramuscular)'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'UGX'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class WeightRecordForm(forms.ModelForm):
    """
    Form for recording weight measurements
    """
    class Meta:
        model = WeightRecord
        fields = ['animal', 'date', 'weight', 'measured_by', 'notes']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kg'}),
            'measured_by': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AnimalSearchForm(forms.Form):
    """
    Simple search form for looking up animals by tag_id
    Used in the QR scanner page
    """
    tag_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter or scan tag ID',
            'id': 'tag_id_input'
        })
    )
