import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

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
    """
    Core animal model - stores basic information about each cattle
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SOLD', 'Sold'),
        ('DECEASED', 'Deceased'),
        ('QUARANTINE', 'Quarantine'),
    ]
    
    BREED_CHOICES = [
        ('BORAN', 'Boran'),
        ('ANKOLE', 'Ankole'),
        ('FRIESIAN', 'Friesian'),
        ('JERSEY', 'Jersey'),
        ('CROSS', 'Cross Breed'),
        ('OTHER', 'Other'),
    ]
    
    # Primary identification
    tag_id = models.CharField(max_length=50, unique=True, help_text="Unique tag/ID for the animal")
    name = models.CharField(max_length=100, blank=True, help_text="Optional name for the animal")
    
    # Basic info
    breed = models.CharField(max_length=50, choices=BREED_CHOICES, default='BORAN')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(help_text="Date of birth")
    
    # Status and location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    ranch_id = models.CharField(max_length=50, default='KISOMBWA_MAIN', help_text="Ranch location identifier")
    
    # Physical attributes
    color = models.CharField(max_length=100, blank=True, help_text="Color/markings description")
    weight_at_birth = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    
    # Relationships
    sire = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_sire', help_text="Father")
    dam = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_as_dam', help_text="Mother")
    
    # IoT Integration (for Member 2)
    collar_id = models.CharField(max_length=50, null=True, blank=True, help_text="Associated IoT collar device ID")
    
    # Media
    photo = models.ImageField(upload_to='animals/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, help_text="Auto-generated QR code")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'
    
    def __str__(self):
        return f"{self.tag_id} - {self.name or 'Unnamed'}"
    
    def age_in_days(self):
        """Calculate animal's age in days"""
        return (timezone.now().date() - self.birth_date).days
    
    def age_display(self):
        """Display age in human-readable format"""
        days = self.age_in_days()
        years = days // 365
        months = (days % 365) // 30
        if years > 0:
            return f"{years} year(s), {months} month(s)"
        elif months > 0:
            return f"{months} month(s)"
        else:
            return f"{days} day(s)"
    
    def generate_qr_code(self):
        """
        Generate QR code containing the animal's tag_id
        This QR code can be scanned to quickly look up the animal
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # The QR code will contain the tag_id
        qr.add_data(self.tag_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model field
        filename = f'qr_{self.tag_id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate QR code"""
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)