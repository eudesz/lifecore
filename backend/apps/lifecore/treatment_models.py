from django.db import models
from django.contrib.auth import get_user_model
from .models import Condition

User = get_user_model()


class Treatment(models.Model):
    """
    Tratamiento farmacológico o intervención clínica de largo plazo.
    """
    STATUS_CHOICES = (
        ('active', 'active'),
        ('discontinued', 'discontinued'),
        ('replaced', 'replaced'),
        ('completed', 'completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # Ej: "Metformina 1000mg"
    medication_type = models.CharField(max_length=64)  # Ej: "antidiabetic"
    condition = models.CharField(max_length=64)  # Ej: "diabetes"
    dosage = models.CharField(max_length=128)  # Ej: "1000mg"
    frequency = models.CharField(max_length=64)  # Ej: "2x/day"
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='active')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'condition', 'status']),
            models.Index(fields=['start_date']),
        ]

class TreatmentCondition(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='condition_links')
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='treatment_links')

    class Meta:
        unique_together = (('treatment', 'condition'),)
        indexes = [
            models.Index(fields=['condition']),
            models.Index(fields=['treatment']),
        ]

class TreatmentLog(models.Model):
    """
    Registro de tomas de medicación para medir adherencia.
    """
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='logs')
    scheduled_date = models.DateTimeField()
    taken_date = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['taken']),
        ]


class TreatmentProgress(models.Model):
    """
    Seguimiento de efectividad y eventos asociados a un tratamiento.
    """
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='progress')
    evaluation_date = models.DateField()
    metrics = models.JSONField(default=dict)  # Ej: {'hba1c_before': 8.9, 'hba1c_after': 7.2}
    effectiveness_score = models.IntegerField()  # 1-10
    side_effects = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['evaluation_date']),
        ]


