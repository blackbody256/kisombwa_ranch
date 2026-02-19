import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.livestock.models import Animal

User = get_user_model()


class Alert(models.Model):
    """System-wide alerts from livestock, IoT devices, and AI predictions"""
    
    ALERT_TYPES = [
        ('health', 'Health Issue'),
        ('vaccination', 'Vaccination Due'),
        ('geofence', 'Geofence Breach'),
        ('battery', 'Low Battery'),
        ('weight', 'Weight Concern'),
        ('estrus', 'Estrus Cycle'),
        ('behavior', 'Abnormal Behavior'),
        ('temperature', 'Temperature Alert'),
        ('device', 'Device Issue'),
        ('prediction', 'AI Prediction'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True,
        help_text='Related animal (optional)'
    )
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPES,
        help_text='Type of alert'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='medium',
        help_text='Alert severity level'
    )
    title = models.CharField(
        max_length=200,
        help_text='Short alert title'
    )
    message = models.TextField(
        help_text='Detailed alert description'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='User has viewed this alert'
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text='Alert issue has been resolved'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When alert was resolved'
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        help_text='User who resolved the alert'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Alert generation timestamp'
    )
    
    # Additional metadata for context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context data'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_resolved', 'severity']),
            models.Index(fields=['alert_type', 'is_resolved']),
            models.Index(fields=['animal', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()}: {self.title}"
    
    @property
    def severity_color(self):
        """Return color code for severity"""
        colors = {
            'low': '#10B981',
            'medium': '#F59E0B',
            'high': '#EF4444',
            'critical': '#DC2626',
        }
        return colors.get(self.severity, '#6B7280')
    
    @property
    def icon(self):
        """Return appropriate icon for alert type"""
        icons = {
            'health': '❤️',
            'vaccination': '💉',
            'geofence': '📍',
            'battery': '🔋',
            'weight': '⚖️',
            'estrus': '🐄',
            'behavior': '⚡',
            'temperature': '🌡️',
            'device': '📱',
            'prediction': '🧠',
        }
        return icons.get(self.alert_type, '🔔')
