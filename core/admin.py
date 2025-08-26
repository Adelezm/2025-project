from django.contrib import admin
from .models import User, Patient, Provider, Appointment, AuditLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("username", "email", "role", "is_active", "is_staff")
	search_fields = ("username", "email")
	list_filter = ("role", "is_active", "is_staff")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ("user", "date_of_birth", "contact_number")
	search_fields = ("user__username", "user__email")


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
	list_display = ("user", "specialty", "license_number")
	search_fields = ("user__username", "license_number", "specialty")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ("patient", "provider", "appointment_datetime", "status", "consultation_type")
	list_filter = ("status", "consultation_type")
	search_fields = ("patient__user__username", "provider__user__username")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ("created_at", "actor", "action", "target_model", "target_id")
	search_fields = ("actor__username", "action", "target_model", "target_id")
	readonly_fields = ("created_at",)
