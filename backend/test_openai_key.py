import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

key = os.getenv('OPENAI_API_KEY', '')
print(f"Clave encontrada: {key[:15]}...{key[-10:]}")
print(f"Longitud: {len(key)}")
print(f"Empieza con 'sk-': {key.startswith('sk-')}")

if key:
    import openai
    openai.api_key = key
    try:
        response = openai.models.list()
        print("✅ API Key válida!")
    except Exception as e:
        print(f"❌ Error: {e}")
