from django.http import JsonResponse
from time import time
from collections import defaultdict

# Very simple in-memory rate limiter (per-process)
_REQUESTS: dict[str, list[float]] = defaultdict(list)

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'same-origin'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        # Basic CSP; adjust as needed
        response['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

class RateLimitMiddleware:
    def __init__(self, get_response, limit_per_minute: int = 120):
        self.get_response = get_response
        self.limit = limit_per_minute

    def __call__(self, request):
        key = request.META.get('HTTP_AUTHORIZATION') or request.META.get('REMOTE_ADDR') or 'anon'
        now = time()
        window_start = now - 60.0
        buf = _REQUESTS[key]
        # prune
        i = 0
        for ts in buf:
            if ts >= window_start:
                break
            i += 1
        if i:
            del buf[:i]
        if len(buf) >= self.limit:
            return JsonResponse({'error': 'rate_limited'}, status=429)
        buf.append(now)
        return self.get_response(request)
