from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ProviderViewSet, AppointmentViewSet, health, request_otp, verify_otp, fhir_patients

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
	path('health/', health, name='health'),
	path('auth/request-otp/', request_otp, name='request_otp'),
	path('auth/verify-otp/', verify_otp, name='verify_otp'),
	path('fhir/Patient', fhir_patients, name='fhir_patients'),
	path('', include(router.urls)),
]