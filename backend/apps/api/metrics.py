from django.http import JsonResponse
from .middleware import _REQUESTS

def metrics_view(request):
    total = sum(len(v) for v in _REQUESTS.values())
    keys = len(_REQUESTS)
    return JsonResponse({'requests_window_60s': total, 'keys_tracked': keys})
