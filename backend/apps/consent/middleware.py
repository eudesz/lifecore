from typing import Any, Dict, Callable


class SmartConsentMiddleware:
    """Middleware de consentimiento (scaffold). Verifica scope/purpose antes de acceder a datos."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        # Aquí se verificaría request.user y scope/purpose
        # Placeholder: permitir paso
        response = self.get_response(request)
        return response


def require_consent(resource: str, purpose: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # TODO: validar consentimiento antes de ejecutar func
            return func(*args, **kwargs)
        return wrapper
    return decorator
