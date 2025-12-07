from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
import json

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body or '{}')
    except Exception:
        data = {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({'error': 'username and password are required'}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'invalid_credentials'}, status=401)
    login(request, user)
    return JsonResponse({'status': 'ok', 'user': {'id': user.id, 'username': user.username}})

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'ok'})

@csrf_exempt
@require_http_methods(["GET"])
def users_list(request):
    """
    Lista usuarios disponibles para selección en la landing page
    (solo para demo, sin contraseña)
    """
    users = User.objects.filter(is_active=True).order_by('username')
    users_data = []
    for user in users:
        # Crear display_name a partir del username
        display_name = user.username.replace('-', ' ').replace('_', ' ').title()
        if user.first_name or user.last_name:
            display_name = f"{user.first_name} {user.last_name}".strip()
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'display_name': display_name
        })
    
    return JsonResponse({'users': users_data})
