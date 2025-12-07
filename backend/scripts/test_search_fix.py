import os
print("Starting script...")
import django
import sys
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()
print("Django setup OK.")

from django.contrib.auth import get_user_model
from apps.agents_v2.views import analyze

User = get_user_model()

def run_test_search():
    username = "alexander_synthetic"
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
    except User.DoesNotExist:
        print("User not found.")
        return

    query = "¿Qué preocupaciones ha mencionado el doctor recurrentemente en sus notas clínicas sobre mi dieta?"
    print(f"\nQuery: {query}")
    try:
        response = analyze({
            'query': query,
            'user_id': user.id,
            'conversation_id': 'test-search'
        })
        print("Response:", response.get('final_text')[:200])
        if response.get('references'):
            print("Tools used:", [r['title'] for r in response['references']])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test_search()

