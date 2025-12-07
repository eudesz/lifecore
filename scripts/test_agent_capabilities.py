import os
import django
import sys
from pathlib import Path

# Setup Django environment
# Current path: backend/scripts/test_agent_capabilities.py
# Backend root: backend/
sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.agents_v2.views import analyze

User = get_user_model()

def run_test_suite():
    # 1. Get or create test user
    username = "alexander_synthetic"
    try:
        user = User.objects.get(username=username)
        print(f"Testing with user: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print(f"User {username} not found. Please run load_full_history.py first.")
        return

    # 2. Define Test Prompts
    test_suite = {
        "A_Trends_Temporal": [
            "¿Cómo ha variado mi peso promedio anual desde que nací hasta hoy?",
            "Muéstrame una gráfica de mi presión arterial (sistólica y diastólica) durante los últimos 5 años.",
            "¿Cuál fue mi nivel de glucosa más alto registrado en la década del 2010?"
        ],
        "B_Event_Correlation": [
            "¿Empezó a bajar mi peso después de que me recetaron Metformina?",
            "¿Cómo estaba mi presión arterial el mes antes de mi diagnóstico de Diabetes Tipo 2?",
            "¿Hubo algún cambio en mis pasos diarios (wearables) después de mi diagnóstico en 2017?"
        ],
        "C_Semantic_Search": [
            "¿Qué preocupaciones ha mencionado el doctor recurrentemente en sus notas clínicas sobre mi dieta?",
            "Busca en los reportes de laboratorio cualquier mención de 'anemia' o 'hierro bajo'.",
            "Resúmeme la evolución de mi estado de ánimo según las transcripciones de las consultas."
        ],
        "D_Pharmacology": [
            "¿Qué medicamentos estoy tomando actualmente y cuál es la dosis?",
            "¿Cuándo fue la última vez que se ajustó mi dosis de Metformina?",
            "Hazme una lista cronológica de todos los tratamientos que he recibido desde los 30 años."
        ],
        "E_Complex_Reasoning": [
            "Analiza mi salud integral en 2019: combina mis laboratorios, notas del doctor y mis signos vitales de ese año.",
            "¿Existe alguna discrepancia entre lo que dicen los reportes de laboratorio (PDFs) y lo que anotó el doctor ese día?",
            "Basado en mi historial de los últimos 50 años, ¿cuáles son mis 3 mayores factores de riesgo actuales?"
        ],
        "F_Curiosity": [
            "¿Cuánto pesaba cuando nací?",
            "¿Cuántos kilómetros he caminado en total en los últimos 10 años (sumando pasos)?",
            "¿Tengo algún vacío de información médica (años sin datos)?"
        ]
    }

    # 3. Run Tests
    print("\nStarting Agent V2 Test Suite...\n" + "="*50)
    
    results = {}
    
    for category, prompts in test_suite.items():
        print(f"\nTesting Category: {category}")
        print("-" * 30)
        
        for i, query in enumerate(prompts, 1):
            print(f"\n[Test {category}-{i}] Query: {query}")
            try:
                # Call the agent
                response = analyze({
                    'query': query,
                    'user_id': user.id,
                    'conversation_id': f'test-suite-{category}'
                })
                
                final_text = response.get('final_text', 'No response text')
                refs = response.get('references', [])
                
                print(f"--> Agent Response ({len(final_text)} chars):")
                print(f"    {final_text[:200]}..." if len(final_text) > 200 else f"    {final_text}")
                
                if refs:
                    print("    > Used Tools/Refs:")
                    for r in refs:
                        print(f"      - {r.get('title', 'Unknown')}")
                else:
                    print("    > No tools used directly (LLM Logic or Error).")
                    
            except Exception as e:
                print(f"--> ERROR: {e}")

    print("\n" + "="*50 + "\nTest Suite Complete.")

if __name__ == "__main__":
    run_test_suite()
