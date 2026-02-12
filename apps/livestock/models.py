from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.core.models import Animal

class HealthRecord(models.Model):
    """
    Tracks health events, diagnoses, and treatments for animals
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    date = models.DateField(default=timezone.now)
    diagnosis = models.CharField(max_length=200, help_text="What was diagnosed")
    symptoms = models.TextField(blank=True, help_text="Observed symptoms")
    treatment = models.TextField(help_text="Treatment administered")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='LOW')
    
    # Cost tracking
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True, help_text="When to check again")
    notes = models.TextField(blank=True)
    
    # Who recorded this
    recorded_by = models.CharField(max_length=100, blank=True, help_text="Veterinarian or staff name")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
    
    def __str__(self):
        return f"{self.animal.tag_id} - {self.diagnosis} ({self.date})"


class Vaccination(models.Model):
    """
    Tracks vaccination history and schedules
    """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=200, help_text="Name of the vaccine")
    disease = models.CharField(max_length=200, blank=True, help_text="Disease prevented")
    
    date_administered = models.DateField(default=timezone.now)
    next_due_date = models.DateField(help_text="When the next dose is due")
    
    batch_number = models.CharField(max_length=100, blank=True, help_text="Vaccine batch number")
    administered_by = models.CharField(max_length=100, blank=True, help_text="Veterinarian or staff name")
    
    dosage = models.CharField(max_length=50, blank=True, help_text="Dosage administered")
    route = models.CharField(max_length=50, blank=True, help_text="Route of administration (e.g., IM, SC)")
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_administered']
        verbose_name = 'Vaccination'
        verbose_name_plural = 'Vaccinations'
    
    def __str__(self):
        return f"{self.animal.tag_id} - {self.vaccine_name} ({self.date_administered})"
    
    def is_due(self):
        """Check if vaccination is due"""
        return timezone.now().date() >= self.next_due_date


class WeightRecord(models.Model):
    """
    Track weight measurements over time for growth monitoring
    """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='weight_records')
    date = models.DateField(default=timezone.now)
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], help_text="Weight in kg")
    
    # Context
    measured_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text="Any observations during weighing")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Weight Record'
        verbose_name_plural = 'Weight Records'
    
    def __str__(self):
        return f"{self.animal.tag_id} - {self.weight}kg ({self.date})"