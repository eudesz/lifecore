from typing import Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from apps.lifecore.models import Observation, Document, TimelineEvent


def _recent_observation(user_id: int, code: str, days: int = 14) -> Optional[Observation]:
    cutoff = timezone.now() - timedelta(days=days)
    return Observation.objects.filter(user_id=user_id, code=code, taken_at__gte=cutoff).order_by('-taken_at').first()


def _recent_event(user_id: int, kind_prefix: str, days: int = 14) -> Optional[TimelineEvent]:
    cutoff = timezone.now() - timedelta(days=days)
    return TimelineEvent.objects.filter(user_id=user_id, kind__startswith=kind_prefix, occurred_at__gte=cutoff).order_by('-occurred_at').first()


def generate_proactive_question(user_id: int) -> Optional[str]:
    """
    Genera una pregunta proactiva basada en contexto reciente del usuario.
    """
    # 1) Cambios en glucosa recientes
    last_glucose = _recent_observation(user_id, 'glucose')
    if last_glucose and last_glucose.value and last_glucose.value > 180:
        return "He notado que tu glucosa estuvo elevada recientemente. ¿Cómo te has sentido estos días?"

    # 2) Inicio/ajuste de tratamiento
    recent_treatment = _recent_event(user_id, 'treatment')
    if recent_treatment:
        return "Veo que hubo un ajuste reciente en tu tratamiento. ¿Has notado algún efecto o cambio desde entonces?"

    # 3) Laboratorio reciente
    recent_lab = _recent_event(user_id, 'lab')
    if recent_lab:
        return "Recientemente registraste un análisis de laboratorio. ¿Te gustaría que revisemos juntos los resultados?"

    # 4) Sin interacciones por varios días
    last_interaction = _recent_event(user_id, 'agents_v2.analyze', days=7)
    if not last_interaction:
        return "Hace días que no conversamos. ¿Cómo te has sentido en términos de estado de ánimo, actividad y adherencia?"

    # 5) Pregunta general
    return "¿Cómo has estado últimamente en actividad física, sueño y estado de ánimo?"


