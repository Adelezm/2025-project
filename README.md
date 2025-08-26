# Telemedicine Secure Communication Backend (MVP)

This repository contains a Django + DRF backend aligned to the analysis/design: custom user with roles, Patients/Providers/Appointments, JWT auth, OTP-based login flow (dev), audit logging middleware, and a minimal FHIR Patient endpoint. Channels ASGI is configured for future WebRTC signaling.

## Prerequisites
- Python 3.13+
- Debian/Ubuntu: `python3-venv` package (already handled by setup below)

## Quick Start
```bash
cd /workspace
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com
# Run server
python manage.py runserver 0.0.0.0:8000
```

## Seed demo patient and test OTP + JWT
```bash
source .venv/bin/activate
python - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","telemed.settings")
import django
django.setup()
from core.models import User, Patient
u, _ = User.objects.get_or_create(username="patient1", defaults={"email":"p1@example.com"})
u.role = User.Role.PATIENT
u.set_password("pass")
u.save()
Patient.objects.get_or_create(user=u)
print("Seeded patient1 / pass")
PY

# Request OTP (returns dev_otp for testing)
curl -sS -X POST http://127.0.0.1:8000/api/auth/request-otp/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"patient1"}'

# Verify OTP (replace CODE with dev_otp value from previous step)
curl -sS -X POST http://127.0.0.1:8000/api/auth/verify-otp/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"patient1","code":"CODE"}'
```
The response includes `{ access, refresh, role }`. Use `access` for Bearer auth.

## Endpoints
- Health: `GET /api/health/`
- JWT: `POST /api/token/`, `POST /api/token/refresh/`
- OTP (dev): `POST /api/auth/request-otp/`, `POST /api/auth/verify-otp/`
- Patients API: `GET/POST/PUT/PATCH/DELETE /api/patients/`
- Providers API: `GET/POST/PUT/PATCH/DELETE /api/providers/`
- Appointments API: `GET/POST/PUT/PATCH/DELETE /api/appointments/`
- FHIR Patient (minimal): `GET /api/fhir/Patient`, `POST /api/fhir/Patient`

All non-public endpoints require `Authorization: Bearer <access>`.

## Admin
- `http://127.0.0.1:8000/admin/` (use superuser created above)

## Notes
- OTP delivery is mocked (returns `dev_otp`); in production replace with SMS/Email provider.
- Audit logs are captured via middleware for `/api/*` and sensitive paths.
- SQLite used for simplicity; switch to PostgreSQL in production.
- Channels in-memory layer is configured; add Redis for production and WebRTC signaling.

## Next Steps
- Frontend (React + Vite + Tailwind) for Patient, Provider, Admin flows
- WebRTC signaling service and TURN fallback for low-bandwidth
- FHIR mappings expansion and EHR integration (SMART on FHIR/OAuth2)
- Row-Level Security patterns if migrating to PostgreSQL
- Security hardening: Argon2, HTTPS/TLS, secrets management, rate limiting 
