import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended user model with ranch-specific fields"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('vet', 'Veterinarian'),
        ('worker', 'Ranch Worker'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'users'

class Ranch(models.Model):
    """Ranch/Farm entity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_ranches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ranches'
        verbose_name_plural = 'Ranches'
    
    def __str__(self):
        return self.name

class Animal(models.Model):
    """Core animal model - Member 1 will extend this"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sick', 'Sick'),
        ('quarantine', 'Quarantine'),
        ('sold', 'Sold'),
        ('deceased', 'Deceased'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Relationships
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, related_name='animals')
    sire = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_sire')
    dam = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_dam')
    
    # Media
    photo = models.ImageField(upload_to='animals/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'animals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tag_id} - {self.name}"
    
    @property
    def age_months(self):
        from datetime import date
        today = date.today()
        return (today.year - self.birth_date.year) * 12 + today.month - self.birth_date.month