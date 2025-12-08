import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory

# Setup Django
sys.path.append(str(os.path.join(os.path.dirname(__file__), '../backend')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from apps.lifecore.views import prompts_intelligent
from django.contrib.auth import get_user_model

User = get_user_model()

def test_view():
    print("Diagnosticando endpoint prompts_intelligent...")
    
    # Buscar usuario
    try:
        user = User.objects.get(username="alexander_synthetic")
        print(f"Usuario encontrado: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print("Usuario no encontrado, usando ID 1 por defecto")
        user = User.objects.first()
        if not user:
            print("CRITICO: No hay usuarios en la BD")
            return

    # Crear request falso con API Key
    factory = RequestFactory()
    # Asumiendo que 'dev-secret-key' es una key válida en settings o environment de prueba,
    # o simulando el comportamiento del middleware auth si existiera.
    # El decorador require_api_key busca HTTP_X_API_KEY
    
    request = factory.get(
        f'/api/prompts/intelligent?user_id={user.id}',
        HTTP_X_API_KEY='dev-secret-key' # Key por defecto en dev
    )
    
    # Simular atributos que pone el middleware
    request._platform_user = user
    request._platform_role = 'patient'
    request._platform_system = True # Bypass scope checks for test
    
    try:
        response = prompts_intelligent(request)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response['Content-Type']}")
        if response.status_code == 200:
            print("CONTENIDO (Inicio):", response.content[:200])
            print("✅ PRUEBA EXITOSA: El código del view funciona correctamente.")
        else:
            print("❌ ERROR: El view devolvió un código de error.")
            print(response.content)
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN NO CAPTURADA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_view()

