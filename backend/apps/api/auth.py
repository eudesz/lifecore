import os
from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from django.db import models

from apps.lifecore.models import ApiClientToken, ConsentPolicy, AuditLog


def require_api_key(view_func):
    system_key = os.getenv('DJANGO_API_KEY')

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Session-auth fallback
        if getattr(request, 'user', None) is not None and request.user.is_authenticated:
            request._platform_user = request.user
            request._platform_role = 'patient'
            request._platform_system = False
            return view_func(request, *args, **kwargs)

        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        token = auth.split(' ', 1)[1].strip()

        if system_key and token == system_key:
            request._platform_user = None
            request._platform_role = 'system'
            request._platform_system = True
            return view_func(request, *args, **kwargs)

        try:
            t = ApiClientToken.objects.get(token=token, active=True)
            if t.expires_at and t.expires_at < timezone.now():
                return JsonResponse({'error': 'Token expired'}, status=401)
            request._platform_user = t.user
            request._platform_role = t.role
            request._platform_system = False
            return view_func(request, *args, **kwargs)
        except ApiClientToken.DoesNotExist:
            return JsonResponse({'error': 'Forbidden'}, status=403)

    return _wrapped


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def audit_access(resource: str, action: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            try:
                response = view_func(request, *args, **kwargs)
                try:
                    AuditLog.objects.create(
                        user=getattr(request, '_platform_user', None),
                        actor_role=getattr(request, '_platform_role', 'unknown'),
                        resource=resource,
                        action=action,
                        success=getattr(response, 'status_code', 500) < 400,
                        status_code=getattr(response, 'status_code', 500),
                        method=request.method,
                        path=request.path,
                        ip=_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except Exception:
                    pass
                return response
            except Exception as e:
                try:
                    AuditLog.objects.create(
                        user=getattr(request, '_platform_user', None),
                        actor_role=getattr(request, '_platform_role', 'unknown'),
                        resource=resource,
                        action=action,
                        success=False,
                        status_code=500,
                        method=request.method,
                        path=request.path,
                        ip=_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        details={'error': str(e)}
                    )
                except Exception:
                    pass
                raise
        return _wrapped
    return decorator


def smart_consent(resource: str, purpose: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            # System bypass
            if getattr(request, '_platform_system', False):
                return view_func(request, *args, **kwargs)
            role = getattr(request, '_platform_role', 'patient')
            # Doctors/Admins bypass explicit consent for now
            if role in ('doctor', 'admin'):
                return view_func(request, *args, **kwargs)
            user = getattr(request, '_platform_user', None)
            if not user:
                return JsonResponse({'error': 'Consent required'}, status=403)
            now = timezone.now()
            allowed = ConsentPolicy.objects.filter(
                user=user, resource=resource, purpose=purpose, allowed=True
            ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)).exists()
            if not allowed:
                try:
                    AuditLog.objects.create(
                        user=user,
                        actor_role=role,
                        resource=resource,
                        action=f'consent:{purpose}',
                        success=False,
                        status_code=403,
                        method=request.method,
                        path=request.path,
                        ip=_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        details={'reason': 'missing_consent'}
                    )
                except Exception:
                    pass
                return JsonResponse({'error': 'Consent required'}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
