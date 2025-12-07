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
    query = (payload or {}).get('query', '')
    user_id_raw = (payload or {}).get('user_id')
    
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

    # 2. Setup Context & Memory
    conversation_id: str = (payload or {}).get('conversation_id') or str(uuid.uuid4())
    context_filters = (payload or {}).get('context_filters') or {}
    
    # Save user message to memory
    try:
        MemoryEpisode.objects.create(
            user_id=resolved_user_id,
            kind='chat',
            content=query or '',
            metadata={'role': 'user', 'conv_id': conversation_id, 'conversation_scope': context_filters}
        )
    except Exception:
        pass

    # 3. Retrieve Conversation History
    history_text = _get_conversation_history(resolved_user_id, conversation_id)

    # 4. Agent Execution Loop (ReAct / Tool Calling)
    # We call the LLM with the user query + tools. It may decide to call a tool or answer directly.
    
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if not openai_key:
        return {'status': 'error', 'final_text': "Error de configuración: falta API Key."}

    try:
        import openai
        openai.api_key = openai_key
        
        system_prompt = f"""Eres un asistente médico inteligente (QuantIA) con acceso a herramientas avanzadas de análisis de datos clínicos (ID: {resolved_user_id}).
        
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

        Reglas:
        - Si preguntan por ANTECEDENTES (familiares o personales):
           a) Usa 'search_medical_documents' buscando "antecedentes", "historia clínica", "familiares".
           b) Usa 'get_clinical_events' para ver diagnósticos pasados.
        - Si preguntan por EVOLUCIÓN de síntomas o condiciones:
           a) Usa 'get_medical_summary_data' con 'condition=X' para ver la historia estructurada.
           b) Usa 'search_medical_documents' buscando el nombre de la condición para ver notas cualitativas de progreso (ej. "evolución", "mejoría", "recaída").
        - Si preguntan por interpretación de análisis de sangre o "labs", USA 'analyze_lab_panels'.
        - Si preguntan "¿Qué riesgo tengo?" o probabilidades futuras, USA 'calculate_risk_scores'.
        - Si preguntan "¿Puedo tomar X con Y?" o interacciones, USA 'check_drug_interactions'.
        - Si preguntan fechas o eventos, USA 'get_clinical_events'.
        - NO inventes datos. Si no hay datos, dilo.
        - Responde en español, profesional y empático.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto previo:\n{history_text}\n\nPregunta actual: {query}"}
        ]

        # First Call: Let LLM decide to use tools
        completion = openai.chat.completions.create(
            model="gpt-4o", # Use a strong model for tool calling
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto"
        )

        response_msg = completion.choices[0].message
        tool_calls = response_msg.tool_calls
        
        final_response_text = ""
        used_refs = []

        if tool_calls:
            # The model wants to use tools. Execute them.
            messages.append(response_msg) # Add the assistant's "intent" to messages
            
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                tool_result = "Error: Tool not found"
                if fn_name in AVAILABLE_TOOLS:
                    try:
                        tool_result = AVAILABLE_TOOLS[fn_name](user_id=resolved_user_id, **fn_args)
                    except Exception as e:
                        tool_result = f"Error executing {fn_name}: {str(e)}"
                
                # Append result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(tool_result)
                })
                
                # Store reference for UI
                used_refs.append({
                    'title': f"Tool: {fn_name}",
                    'source': 'System',
                    'snippet': str(tool_result)[:200] + "..."
                })

            # Second Call: Get final answer based on tool results
            final_completion = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_response_text = final_completion.choices[0].message.content

        else:
            # No tools needed, just chat
            final_response_text = response_msg.content

        # 5. Save Response & Return
        MemoryEpisode.objects.create(
            user_id=resolved_user_id,
            kind='chat',
            content=final_response_text,
            metadata={'role': 'assistant', 'conv_id': conversation_id, 'tools_used': [t.function.name for t in (tool_calls or [])]}
        )

        return {
            'status': 'success',
            'final_text': final_response_text,
            'conversation_id': conversation_id,
            'references': used_refs
        }

    except Exception as e:
        # Fallback in case of critical failure
        print(f"Agent Error: {e}")
        return {'status': 'error', 'final_text': "Lo siento, tuve un problema interno al procesar tu solicitud."}


def _get_conversation_history(user_id: int, conv_id: str) -> str:
    try:
        episodes = MemoryEpisode.objects.filter(
            user_id=user_id,
            kind='chat',
            metadata__conv_id=conv_id
        ).order_by('-occurred_at')[:5] # Last 5 turns
        
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

