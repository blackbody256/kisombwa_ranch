from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class MLModel(models.Model):
    """
    Stores ML models used for predictions
    """
    MODEL_TYPE_CHOICES = [
        ('health', 'Health Prediction'),
        ('behavior', 'Behavior Analysis'),
        ('estrus', 'Estrus Detection'),
        ('anomaly', 'Anomaly Detection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Model name (e.g., health_v1)")
    version = models.CharField(max_length=20, help_text="Model version")
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    model_file = models.CharField(max_length=200, help_text="Path to saved model file")
    accuracy = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Model accuracy score (0.0-1.0)"
    )
    is_active = models.BooleanField(default=True, help_text="Currently in use")
    description = models.TextField(blank=True, help_text="Model description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ml_models'
        ordering = ['-created_at']
        verbose_name = 'ML Model'
        verbose_name_plural = 'ML Models'
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.model_type})"


class Prediction(models.Model):
    """
    Stores predictions made by ML models
    """
    PREDICTION_TYPE_CHOICES = [
        ('health', 'Health Prediction'),
        ('behavior', 'Behavior Prediction'),
        ('estrus', 'Estrus Detection'),
        ('anomaly', 'Anomaly Detection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(
        'livestock.Animal',
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Prediction subject"
    )
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPE_CHOICES)
    model_name = models.CharField(max_length=100, help_text="Model used")
    model_version = models.CharField(max_length=20, help_text="Model version")
    predicted_value = models.CharField(
        max_length=100,
        help_text="Prediction result (e.g., 'SICK', 'GRAZING')"
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence (0.0-1.0)"
    )
    input_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Input features used for prediction"
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional context and information"
    )
    predicted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'predictions'
        ordering = ['-predicted_at']
        indexes = [
            models.Index(fields=['animal', '-predicted_at'], name='animal_pred_idx'),
            models.Index(fields=['predicted_at'], name='pred_time_idx'),
            models.Index(fields=['prediction_type', 'predicted_at'], name='pred_type_time_idx'),
        ]
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
    
    def __str__(self):
        return f"{self.animal.tag_id} - {self.prediction_type}: {self.predicted_value} ({self.confidence_score:.2%})"
    
    @property
    def is_high_confidence(self):
        """Check if prediction has high confidence (>= 80%)"""
        return self.confidence_score >= 0.80
