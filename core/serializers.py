from rest_framework import serializers
from .models import User, Patient, Provider, Appointment


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["id", "username", "email", "first_name", "last_name", "role"]
		read_only_fields = ["id", "role"]


class PatientSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')

	class Meta:
		model = Patient
		fields = ["id", "user", "user_id", "date_of_birth", "contact_number", "address", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at", "user"]


class ProviderSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')

	class Meta:
		model = Provider
		fields = ["id", "user", "user_id", "specialty", "license_number", "contact_number", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at", "user"]


class AppointmentSerializer(serializers.ModelSerializer):
	patient = PatientSerializer(read_only=True)
	provider = ProviderSerializer(read_only=True)
	patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), write_only=True, source='patient')
	provider_id = serializers.PrimaryKeyRelatedField(queryset=Provider.objects.all(), write_only=True, source='provider')

	class Meta:
		model = Appointment
		fields = [
			"id",
			"patient",
			"provider",
			"patient_id",
			"provider_id",
			"appointment_datetime",
			"duration_minutes",
			"status",
			"consultation_type",
			"notes",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_at", "updated_at", "patient", "provider"]