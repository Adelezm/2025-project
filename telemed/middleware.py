from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.urls import resolve
from core.models import AuditLog


class AuditMiddleware(MiddlewareMixin):
	SENSITIVE_PATHS = ("/admin/", "/api/token/", "/api/auth/")

	def process_view(self, request, view_func, view_args, view_kwargs):
		request._view_name = getattr(view_func, "__name__", str(view_func))
		return None

	def process_response(self, request, response):
		try:
			path = request.path
			if any(path.startswith(p) for p in self.SENSITIVE_PATHS) or path.startswith("/api/"):
				user = getattr(request, "user", None)
				AuditLog.objects.create(
					actor=user if getattr(user, "is_authenticated", False) else None,
					action=f"{request.method} {getattr(request, '_view_name', resolve(path).url_name) or path}",
					target_model="",
					target_id="",
					metadata={"status_code": response.status_code},
					ip_address=request.META.get("REMOTE_ADDR"),
					user_agent=request.META.get("HTTP_USER_AGENT", ""),
				)
		except Exception:
			pass
		return response