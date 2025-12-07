#!/usr/bin/env python3
"""
Agente de test conversacional que usa LLM para generar preguntas de seguimiento.
Mantiene contexto y conversation_id a lo largo de 10 turnos.
"""
import os
import json
import uuid
import requests
from typing import List, Dict
from pathlib import Path

# Cargar variables de .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Cargando configuración desde: {env_path}")
except ImportError:
    print("⚠️  python-dotenv no instalado, usando variables de entorno del sistema")

BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')
API_KEY = os.getenv('DJANGO_API_KEY', 'dev-secret-key')
OPENAI_KEY = os.getenv('OPENAI_API_KEY', '')


def call_assistant(query: str, user_id: str, conversation_id: str) -> Dict:
    """Llama al asistente LifeCore."""
    payload = {'query': query, 'user_id': user_id, 'conversation_id': conversation_id}
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    r = requests.post(f'{BACKEND}/api/agents/v2/analyze', data=json.dumps(payload), headers=headers)
    r.raise_for_status()
    return r.json()


def generate_next_question(history: List[Dict], use_openai: bool = True) -> str:
    """
    Usa un LLM para generar la siguiente pregunta con contexto.
    Si OPENAI_API_KEY no está disponible, usa reglas simples.
    """
    if use_openai and OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            
            # Construir contexto de la conversación
            context = "Conversación previa:\n"
            for turn in history[-3:]:  # Últimos 3 turnos
                context += f"Usuario: {turn['user']}\nAsistente: {turn['assistant'][:200]}...\n\n"
            
            system_prompt = """Eres un paciente con diabetes que habla con su asistente médico.
Haz preguntas de seguimiento naturales basándote en las respuestas previas.
Mantén el contexto y pregunta sobre:
- Detalles de los valores mencionados
- Comparaciones temporales
- Correlaciones con otros parámetros
- Hábitos y estilo de vida
- Adherencia al tratamiento
Haz UNA pregunta breve y natural."""
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context + "\n¿Qué pregunta harías a continuación?"}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️  OpenAI falló ({e}), usando reglas simples")
            use_openai = False
    
    # Fallback: reglas simples basadas en contexto
    if not history:
        return "¿Cuál fue mi último valor de glucosa?"
    
    last_assistant = history[-1]['assistant'].lower()
    
    # Detectar temas en la última respuesta
    if 'glucosa' in last_assistant or 'glucose' in last_assistant:
        return "¿Cómo evolucionó en los últimos 90 días?"
    elif 'evolución' in last_assistant or 'tendencia' in last_assistant:
        return "¿Hay correlación con mi peso?"
    elif 'correlación' in last_assistant or 'peso' in last_assistant:
        return "¿Y con mi presión arterial?"
    elif 'presión' in last_assistant:
        return "¿Mi adherencia a la medicación fue constante?"
    elif 'adherencia' in last_assistant or 'medicación' in last_assistant:
        return "¿Cómo está mi estado de ánimo últimamente?"
    elif 'ánimo' in last_assistant or 'mood' in last_assistant:
        return "¿Mis hábitos de sueño afectan la glucosa?"
    elif 'sueño' in last_assistant:
        return "Resume mis mejores y peores semanas"
    elif 'semanas' in last_assistant or 'mejor' in last_assistant:
        return "¿Qué documentos de laboratorio tengo?"
    else:
        return "Dame un resumen general de mi salud este año"


def run_conversational_test(user_id: str = 'demo-alex', num_turns: int = 10):
    """Ejecuta una conversación de N turnos con contexto."""
    conversation_id = str(uuid.uuid4())
    history: List[Dict] = []
    
    print(f"\n{'='*80}")
    print(f"🤖 TEST CONVERSACIONAL FLUIDO - {num_turns} turnos")
    print(f"Usuario: {user_id} | Conversación: {conversation_id[:8]}...")
    print(f"{'='*80}\n")
    
    use_openai = bool(OPENAI_KEY)
    if use_openai:
        print("✅ Usando OpenAI para generar preguntas\n")
    else:
        print("⚠️  OPENAI_API_KEY no encontrada, usando reglas simples\n")
    
    for i in range(num_turns):
        # Generar pregunta
        if i == 0:
            query = "Hola, ¿cuál fue mi último valor de glucosa?"
        else:
            query = generate_next_question(history, use_openai=use_openai)
        
        print(f"\n{'─'*80}")
        print(f"👤 TURNO {i+1}/{num_turns}")
        print(f"{'─'*80}")
        print(f"Usuario: {query}")
        
        # Llamar asistente
        try:
            response = call_assistant(query, user_id, conversation_id)
            assistant_reply = response.get('final_text', 'Sin respuesta')
            references = response.get('references', [])
            
            print(f"\n🤖 Asistente: {assistant_reply}")
            
            if references:
                print(f"\n📚 Referencias: {len(references)}")
                for idx, ref in enumerate(references[:2], 1):
                    print(f"  [{idx}] {ref.get('title', 'Doc')} - {ref.get('snippet', '')[:60]}...")
            
            # Guardar en historial
            history.append({
                'user': query,
                'assistant': assistant_reply,
                'references': references
            })
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETADO - {len(history)} turnos exitosos")
    print(f"{'='*80}\n")
    
    # Resumen
    print("\n📊 RESUMEN DE LA CONVERSACIÓN:\n")
    for i, turn in enumerate(history, 1):
        print(f"{i}. U: {turn['user'][:60]}...")
        print(f"   A: {turn['assistant'][:80]}...\n")
    
    return history


def export_to_markdown(history: List[Dict], user_id: str, output_file: str = None) -> str:
    """
    Exporta el historial de conversación a formato Markdown.
    """
    from datetime import datetime
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"conversation_{user_id}_{timestamp}.md"
    
    # Construir contenido Markdown
    content = f"""# Test Conversacional - LifeCore Assistant

**Usuario:** `{user_id}`  
**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total de turnos:** {len(history)}

---

"""
    
    for i, entry in enumerate(history, 1):
        user_msg = entry['user']
        assistant_msg = entry['assistant']
        references = entry.get('references', [])
        
        content += f"## Turno {i}\n\n"
        content += f"### 👤 Usuario\n\n{user_msg}\n\n"
        content += f"### 🤖 Asistente\n\n{assistant_msg}\n\n"
        
        if references:
            content += f"#### 📚 Referencias ({len(references)})\n\n"
            for j, ref in enumerate(references, 1):
                title = ref.get('title', 'Sin título')
                snippet = ref.get('snippet', 'Sin contenido')
                source = ref.get('source', 'Desconocido')
                content += f"{j}. **{title}**\n"
                content += f"   - Fuente: `{source}`\n"
                content += f"   - Extracto: _{snippet}_\n\n"
        
        content += "---\n\n"
    
    # Agregar resumen al final
    content += f"## 📊 Resumen\n\n"
    content += f"- **Total de turnos:** {len(history)}\n"
    content += f"- **Usuario:** {user_id}\n"
    content += f"- **Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Escribir archivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file


if __name__ == '__main__':
    import sys
    
    user_id = sys.argv[1] if len(sys.argv) > 1 else 'demo-alex'
    num_turns = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if not OPENAI_KEY:
        print("\n💡 Tip: Agrega OPENAI_API_KEY=sk-... en .env para usar GPT en vez de reglas simples\n")
    
    try:
        history = run_conversational_test(user_id, num_turns)
        
        # Exportar a Markdown
        md_file = export_to_markdown(history, user_id)
        print(f"\n📄 Conversación exportada a: {md_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

