from typing import Any, Dict, Optional, List, Tuple
import uuid
import os
import json
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import QuerySet, Count
import math

from apps.lifecore.models import TimelineEvent, Observation, Document, DocumentChunk, MemoryEpisode, MemorySemantic, Condition, EventCondition
from apps.lifecore.treatment_models import Treatment, TreatmentCondition
from apps.api.flags import is_enabled
from apps.lifecore.embedding import text_to_embedding, cosine_similarity
from apps.lifecore.vectorstore_faiss import FaissVectorStore
from apps.agents_v2.proactive_agent import generate_proactive_question
from apps.lifecore.models import TimelineEvent, Document
from apps.agents_v2.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS

def analyze(payload: Dict[str, Any], request=None) -> Dict[str, Any]:
    """
    Main entry point for agent analysis.
    Uses OpenAI's Function Calling (Tools) to decide how to retrieve information.
    """
    payload = payload or {}
    query = payload.get('query', '')
    user_id_raw = payload.get('user_id')
    
    # 1. Resolve User ID
    resolved_user_id: Optional[int] = None
    user_obj = None
    if user_id_raw is not None:
        try:
            resolved_user_id = int(user_id_raw)
        except Exception:
            if isinstance(user_id_raw, str) and user_id_raw.startswith('demo'):
                User = get_user_model()
                user_obj, _ = User.objects.get_or_create(username=user_id_raw)
                resolved_user_id = user_obj.id
    
    if not resolved_user_id:
        return {'status': 'error', 'final_text': "Falta 'user_id' para realizar el análisis."}

    # Detect caller role / context (patient vs doctor)
    actor_role: str = getattr(request, '_platform_role', 'patient') if request is not None else 'patient'
    doctor_token: Optional[str] = payload.get('doctor_token')

    # 2. Setup Context & Memory
    conversation_id: str = payload.get('conversation_id') or str(uuid.uuid4())
    context_filters = payload.get('context_filters') or {}
    
    # Save user message to memory
    try:
        meta: Dict[str, Any] = {
            'role': 'doctor' if actor_role == 'doctor' else 'user',
            'conv_id': conversation_id,
            'conversation_scope': context_filters,
        }
        if doctor_token and actor_role == 'doctor':
            meta['doctor_token'] = doctor_token
        MemoryEpisode.objects.create(
            user_id=resolved_user_id,
            kind='chat',
            content=query or '',
            metadata=meta,
        )
    except Exception:
        pass

    # 3. Retrieve Conversation History
    history_text = _get_conversation_history(resolved_user_id, conversation_id)

    # 4. Agent Execution Loop (ReAct / Tool Calling)
    
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if not openai_key:
        return {'status': 'error', 'final_text': "Error de configuración: falta API Key."}

    try:
        import openai
        openai.api_key = openai_key
        
        # Tailor behavior depending on who is chatting with the agent
        if actor_role == 'doctor':
            system_prompt = f"""Eres un asistente clínico avanzado (QuantIA) para apoyar a profesionales de la salud.
Tu contexto de datos está ligado a un paciente concreto (ID interno: {resolved_user_id}).
        
        Tus capacidades:
        1. Consultar datos biométricos y tendencias -> 'get_biometric_data'
        2. Consultar eventos clínicos (diagnósticos, cirugías) -> 'get_clinical_events'
        3. Buscar en documentos médicos (cualitativo) -> 'search_medical_documents'
        4. Generar resúmenes completos -> 'get_medical_summary_data'
        5. Comparar métricas entre años (ej. 2020 vs 2021) -> 'compare_health_periods'
        6. Analizar correlaciones (ej. peso vs pasos) -> 'analyze_correlation'
        7. Analizar impacto de tratamientos (antes/después) -> 'analyze_treatment_impact'
        8. Calcular scores de salud (IMC) -> 'calculate_health_score'
        9. Analizar paneles de laboratorio (detectar anomalías) -> 'analyze_lab_panels'
        10. Calcular riesgo cardiovascular/diabetes -> 'calculate_risk_scores'
        11. Verificar seguridad de medicamentos -> 'check_drug_interactions'
        12. Analizar calidad de sueño y descanso -> 'analyze_sleep_quality'
        13. Analizar métricas avanzadas (HRV, VO2 Max) -> 'analyze_wearable_metrics'
        14. Consultar hábitos nutricionales o dieta -> 'analyze_nutritional_logs'
        15. Explorar conexiones en el grafo de conocimiento del paciente -> 'graph_explain_relationship'

Reglas para modo MÉDICO:
- Asume que la persona que pregunta es un profesional sanitario.
- Puedes usar lenguaje técnico (p.ej., SLE, RR, IC, comorbilidad), pero sé claro y estructurado.
- Centra las respuestas en: estratificación de riesgo, contexto clínico, patrones en los datos y limitaciones de los mismos.
- No des recomendaciones de práctica clínica como si fueran guías oficiales; formula sugerencias como apoyo a la decisión, siempre recordando que la decisión final es del clínico.
- Si faltan datos o hay posible sesgo, explícalo de forma explícita.
- Si la pregunta es de tipo causal o más allá de la evidencia disponible, indícalo claramente y evita sobre-interpretar.

Reglas de uso de herramientas (igual que en modo paciente, pero pensando en uso profesional):
        - Si preguntan por ANTECEDENTES (familiares o personales):
           a) Usa 'search_medical_documents' buscando "antecedentes", "historia clínica", "familiares".
           b) Usa 'get_clinical_events' para ver diagnósticos pasados.
        - Si preguntan por EVOLUCIÓN de síntomas o condiciones:
           a) Usa 'get_medical_summary_data' con 'condition=X' para ver la historia estructurada.
           b) Usa 'search_medical_documents' buscando el nombre de la condición para ver notas cualitativas de progreso (ej. "evolución", "mejoría", "recaída").
        - Si preguntan por interpretación de análisis de sangre o "labs", USA 'analyze_lab_panels'.
- Si preguntan "¿Qué riesgo tiene?" o probabilidades futuras, USA 'calculate_risk_scores'.
- Si preguntan "¿Puedo combinar X con Y?" o interacciones, USA 'check_drug_interactions'.
- Si preguntan por SUEÑO, descanso, insomnio o "cómo duerme el paciente", USA 'analyze_sleep_quality'.
        - Si preguntan por fitness avanzado (VO2, HRV, variabilidad cardiaca, esfuerzo), USA 'analyze_wearable_metrics'.
- Si preguntan por DIETA, nutrición, calorías o "qué come", USA 'analyze_nutritional_logs'.
- Si preguntan "¿Cómo se relacionan X, Y y Z en este caso?" (ej. lupus, pancreatitis, proteinuria, trombosis) USA 'graph_explain_relationship' pasando la lista de entidades.
        - Si preguntan fechas o eventos, USA 'get_clinical_events'.
- NO inventes datos. Si no hay datos suficientes, dilo y explica por qué.
- Responde SIEMPRE en español, de forma clara, concisa y orientada a soporte de decisión clínica.
"""
        else:
            system_prompt = f"""Eres un asistente de salud personalizado (QuantIA) para pacientes, con acceso a sus datos clínicos (ID interno: {resolved_user_id}).

Tus capacidades de análisis interno (no las menciones como nombres de herramientas al paciente):
1. Consultar datos biométricos y tendencias.
2. Consultar eventos clínicos (diagnósticos, cirugías).
3. Buscar en documentos médicos (informes, notas).
4. Generar resúmenes completos de la historia.
5. Comparar métricas entre años.
6. Analizar correlaciones sencillas (ej. pasos vs peso).
7. Analizar impacto de tratamientos (antes/después).
8. Calcular scores simples de salud (IMC).
9. Analizar paneles de laboratorio y marcar valores fuera de rango.
10. Calcular riesgos simplificados (cardiovascular, diabetes).
11. Verificar interacciones potenciales entre medicamentos.
12. Analizar sueño y descanso.
13. Analizar métricas avanzadas de wearables.
14. Explorar conexiones en el grafo de conocimiento del paciente.

Reglas para modo PACIENTE:
- Explica TODO en lenguaje sencillo, evitando jerga técnica. Si usas un término médico (p.ej. "proteinuria"), añade enseguida una explicación corta en palabras simples.
- NO des diagnósticos ni confirmes enfermedades: en su lugar, explica qué significan los datos y anima a consultar con su médico.
- NO indiques cambios concretos de medicación (subir/bajar dosis, empezar/suspender fármacos). En su lugar, sugiere preguntas que la persona pueda llevar a su médico.
- Incluye cuando sea relevante una frase recordando que la herramienta no sustituye una consulta médica presencial.
- Si los datos son incompletos o inciertos, dilo explícitamente.

Reglas de uso de herramientas:
- Si preguntan por ANTECEDENTES:
   a) Usa internamente búsqueda en documentos y eventos clínicos.
- Si preguntan por EVOLUCIÓN de síntomas o condiciones:
   a) Usa un resumen de eventos y notas relacionadas con esa condición.
- Si preguntan por análisis de sangre o "labs", usa el módulo de análisis de laboratorios.
- Si preguntan "¿Qué riesgo tengo?" o probabilidades futuras, usa los módulos de riesgo pero expresa el resultado en términos sencillos (por ejemplo: "más alto", "similar", "bajo") y nunca como certeza.
- Si preguntan "¿Puedo tomar X con Y?", revisa interacciones y explícalas en lenguaje llano, insistiendo en hablar con el médico antes de hacer cambios.
- Si preguntan por SUEÑO, fitness o DIETA, usa los módulos correspondientes y ofrece consejos generales y prudentes, no planes de tratamiento personalizados.
- Si preguntan "¿Cómo se relacionan X, Y y Z en mi caso?", usa el grafo de conocimiento, pero explica las relaciones en términos narrativos fáciles de entender.
- NO inventes datos. Si no encuentras información en la historia, dilo claramente.
- Responde SIEMPRE en español, de forma cercana, empática y clara.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto previo:\n{history_text}\n\nPregunta actual: {query}"}
        ]

        # First Call
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto"
        )

        response_msg = completion.choices[0].message
        tool_calls = response_msg.tool_calls
        
        final_response_text = ""
        used_refs = []

        if tool_calls:
            # The model wants to use tools
            messages.append(response_msg)
            
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                tool_result = "Error: Tool not found"
                if fn_name in AVAILABLE_TOOLS:
                    try:
                        tool_result = AVAILABLE_TOOLS[fn_name](user_id=resolved_user_id, **fn_args)
                    except Exception as e:
                        tool_result = f"Error executing {fn_name}: {str(e)}"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(tool_result)
                })
                
                used_refs.append({
                    'title': f"Tool: {fn_name}",
                    'source': 'System',
                    'snippet': str(tool_result)[:200] + "..."
                })

            final_completion = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_response_text = final_completion.choices[0].message.content

        else:
            final_response_text = response_msg.content

        # 5. Save Response & Return
        # Persist assistant response with appropriate role and doctor token (if applicable)
        resp_meta: Dict[str, Any] = {
            'role': 'assistant_doctor' if actor_role == 'doctor' else 'assistant',
            'conv_id': conversation_id,
            'tools_used': [t.function.name for t in (tool_calls or [])],
        }
        if doctor_token and actor_role == 'doctor':
            resp_meta['doctor_token'] = doctor_token
        MemoryEpisode.objects.create(
            user_id=resolved_user_id,
            kind='chat',
            content=final_response_text,
            metadata=resp_meta,
        )

        return {
            'status': 'success',
            'final_text': final_response_text,
            'conversation_id': conversation_id,
            'references': used_refs
        }

    except Exception as e:
        print(f"Agent Error: {e}")
        return {'status': 'error', 'final_text': "Lo siento, tuve un problema interno al procesar tu solicitud."}


def _get_conversation_history(user_id: int, conv_id: str) -> str:
    try:
        episodes = MemoryEpisode.objects.filter(
            user_id=user_id,
            kind='chat',
            metadata__conv_id=conv_id
        ).order_by('-occurred_at')[:5]
        
        history = []
        for ep in reversed(episodes):
            role = ep.metadata.get('role', 'unknown')
            content = ep.content
            history.append(f"{role}: {content}")
        return "\n".join(history)
    except Exception:
        return ""

def status() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'mode': 'agent_v2_tools',
        'tools_loaded': list(AVAILABLE_TOOLS.keys())
    }

