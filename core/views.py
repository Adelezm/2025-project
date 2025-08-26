from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random
from .models import Patient, Provider, Appointment, User
from .serializers import PatientSerializer, ProviderSerializer, AppointmentSerializer


# Create your views here.


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
	return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def request_otp(request):
	username = request.data.get("username")
	if not username:
		return Response({"detail": "username required"}, status=status.HTTP_400_BAD_REQUEST)
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)
	code = f"{random.randint(0, 999999):06d}"
	user.otp_code = code
	user.otp_expires_at = timezone.now() + timedelta(minutes=5)
	user.save(update_fields=["otp_code", "otp_expires_at"])
	# NOTE: In production, send via SMS/Email provider. For now, return masked indicator.
	return Response({"detail": "OTP sent", "dev_otp": code})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
	username = request.data.get("username")
	code = request.data.get("code")
	if not username or not code:
		return Response({"detail": "username and code required"}, status=status.HTTP_400_BAD_REQUEST)
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({"detail": "invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
	if not user.otp_code or not user.otp_expires_at:
		return Response({"detail": "no active otp"}, status=status.HTTP_400_BAD_REQUEST)
	if user.otp_expires_at < timezone.now() or user.otp_code != code:
		return Response({"detail": "invalid or expired otp"}, status=status.HTTP_400_BAD_REQUEST)
	# clear otp and issue JWT
	user.otp_code = ""
	user.otp_expires_at = None
	user.save(update_fields=["otp_code", "otp_expires_at"])
	refresh = RefreshToken.for_user(user)
	return Response({"refresh": str(refresh), "access": str(refresh.access_token), "role": user.role})


class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class PatientViewSet(viewsets.ModelViewSet):
	queryset = Patient.objects.select_related("user").all()
	serializer_class = PatientSerializer
	permission_classes = [permissions.IsAuthenticated]


class ProviderViewSet(viewsets.ModelViewSet):
	queryset = Provider.objects.select_related("user").all()
	serializer_class = ProviderSerializer
	permission_classes = [permissions.IsAuthenticated]


class AppointmentViewSet(viewsets.ModelViewSet):
	queryset = Appointment.objects.select_related("patient__user", "provider__user").all()
	serializer_class = AppointmentSerializer
	permission_classes = [permissions.IsAuthenticated]


# Minimal FHIR Patient mapping (very simplified)
@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def fhir_patients(request):
	if request.method == "GET":
		resources = []
		for p in Patient.objects.select_related("user").all():
			resources.append({
				"resourceType": "Patient",
				"id": str(p.id),
				"name": [{"text": p.user.get_full_name() or p.user.username}],
				"telecom": [{"system": "phone", "value": p.contact_number}] if p.contact_number else [],
				"birthDate": p.date_of_birth.isoformat() if p.date_of_birth else None,
			})
		return Response({"resourceType": "Bundle", "type": "collection", "entry": [{"resource": r} for r in resources]})
	# POST create from FHIR-like payload
	data = request.data
	name = (data.get("name") or [{}])[0]
	display_name = name.get("text") or ""
	contact = None
	for t in data.get("telecom", []):
		if t.get("system") == "phone":
			contact = t.get("value")
			break
	user = User.objects.create(username=f"patient_{timezone.now().timestamp()}"[:30], first_name=display_name)
	user.role = User.Role.PATIENT
	user.save(update_fields=["role", "first_name"])
	patient = Patient.objects.create(user=user, contact_number=contact)
	return Response({"resourceType": "Patient", "id": str(patient.id)}, status=status.HTTP_201_CREATED)
