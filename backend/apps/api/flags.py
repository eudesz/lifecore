import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


def _to_bool(val: str) -> bool:
    return str(val or '').strip().lower() in ('1', 'true', 'yes', 'on')


def is_enabled(name: str) -> bool:
    if name.upper() == 'RAG':
        return _to_bool(os.getenv('FEATURE_RAG', 'true'))
    if name.upper() == 'PROACTIVITY':
        return _to_bool(os.getenv('FEATURE_PROACTIVITY', 'true'))
    return False


def all_flags() -> dict:
    return {
        'RAG': is_enabled('RAG'),
        'PROACTIVITY': is_enabled('PROACTIVITY'),
    }


@csrf_exempt
@require_http_methods(["GET"])
def flags_view(_request):
    return JsonResponse({'flags': all_flags()})


