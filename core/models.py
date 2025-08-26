from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        PROVIDER = "provider", "Provider"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )
    otp_code = models.CharField(max_length=6, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class Patient(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class Provider(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='provider_profile')
    specialty = models.CharField(max_length=128, blank=True)
    license_number = models.CharField(max_length=128, blank=True)
    contact_number = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Provider: {self.user.get_full_name() or self.user.username}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class ConsultationType(models.TextChoices):
        VIDEO = "video", "Video"
        AUDIO = "audio", "Audio"
        CHAT = "chat", "Chat"

    patient = models.ForeignKey('core.Patient', on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey('core.Provider', on_delete=models.CASCADE, related_name='appointments')
    appointment_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    consultation_type = models.CharField(max_length=20, choices=ConsultationType.choices, default=ConsultationType.VIDEO)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Appt {self.id} {self.patient} with {self.provider} at {self.appointment_datetime}"


class AuditLog(models.Model):
    actor = models.ForeignKey('core.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_logs')
    action = models.CharField(max_length=128)
    target_model = models.CharField(max_length=128, blank=True)
    target_id = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.created_at} {self.actor} {self.action} {self.target_model}:{self.target_id}"
