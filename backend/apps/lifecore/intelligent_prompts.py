"""
Sistema de Generación de Prompts Inteligentes
Analiza datos del usuario y genera preguntas personalizadas
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.models import Observation, Document, Condition, TimelineEvent
from django.utils import timezone
from django.contrib.auth.models import User


def analyze_user_health_profile(user_id: int) -> Dict[str, Any]:
    """
    Analiza el perfil completo de salud del usuario y genera prompts inteligentes.
    Incluye: Resúmenes temporales, por condición y por tipo de dato.
    """
    user = User.objects.get(id=user_id)
    
    profile = {
        'user_id': user_id,
        'username': user.username,
        'data_availability': {},
        'categories': [],
        'intelligent_prompts': []
    }
    
    all_prompts = []
    
    # 1. PROMPTS DE RESUMEN TEMPORAL (1, 3, 5 Años)
    # Verificar antigüedad de datos
    try:
        oldest_event = TimelineEvent.objects.filter(user_id=user_id).order_by('occurred_at').first()
        if oldest_event and oldest_event.occurred_at:
            occurred = oldest_event.occurred_at
            if timezone.is_naive(occurred):
                occurred = timezone.make_aware(occurred)
            
            now = timezone.now()
            years_history = (now - occurred).days / 365.0
            
            if years_history >= 1:
                all_prompts.append({
                    'prompt': 'Resumen de mi salud: últimos 12 meses',
                    'category': 'summary',
            'type': 'temporal',
            'priority': 'high',
                    'emoji': '📅',
                    'insight': 'Visión general del último año',
                    'score': 1.0
                })
            
            if years_history >= 3:
                all_prompts.append({
                    'prompt': 'Resumen de historial: últimos 3 años',
                    'category': 'summary',
        'type': 'temporal',
        'priority': 'medium',
                    'emoji': '📅',
                    'insight': 'Evolución a mediano plazo',
                    'score': 0.9
                })
                
            if years_history >= 5:
                all_prompts.append({
                    'prompt': 'Resumen de historial: últimos 5 años',
                    'category': 'summary',
        'type': 'temporal',
        'priority': 'medium',
                    'emoji': '📅',
                    'insight': 'Tendencias de largo plazo',
                    'score': 0.85
                })
    except Exception as e:
        print(f"Error calculating history prompts: {e}")

    # 2. PROMPTS POR DOLENCIA (CONDICIÓN)
    # Finding conditions linked to user's events
    conditions = Condition.objects.filter(event_links__event__user_id=user_id).distinct()
    for cond in conditions:
        all_prompts.append({
            'prompt': f'Resumen de mi historial de {cond.name}',
            'category': 'condition',
        'type': 'analysis',
            'priority': 'high',
            'emoji': '🏥',
            'insight': f'Evolución específica de {cond.name}',
            'score': 0.95
        })

    # 3. PROMPTS POR TIPO DE DATO (Consultas, Labs, Diagnósticos)
    data_types = [
        ('consultation', 'Consultas Médicas', '👨‍⚕️'),
        ('lab', 'Laboratorios', '🧪'),
        ('diagnosis', 'Diagnósticos', '📋'),
        ('treatment', 'Tratamientos', '💊')
    ]
    
    for cat_slug, label, emoji in data_types:
        count = TimelineEvent.objects.filter(user_id=user_id, category=cat_slug).count()
        if count > 0:
            all_prompts.append({
                'prompt': f'Resumen de {label} ({count} eventos)',
                'category': 'summary',
                'type': 'informational',
                'priority': 'medium',
                'emoji': emoji,
                'insight': f'Historial completo de {label.lower()}',
                'score': 0.8
            })

    # 4. PROMPTS CURADOS (Originales)
    # Mantener algunos prompts específicos de métricas si hay datos recientes
    recent_glucose = Observation.objects.filter(user_id=user_id, code='glucose').last()
    if recent_glucose:
         all_prompts.append({
            'prompt': '¿Cómo ha variado mi glucosa este año?',
            'category': 'glucose',
            'type': 'analysis',
            'priority': 'medium',
            'emoji': '🩸',
            'insight': 'Análisis detallado de glucosa',
            'score': 0.75
        })

    # Priorizar y limitar
    profile['intelligent_prompts'] = prioritize_prompts(all_prompts, max_prompts=8)
    
    # Generate stats for summary
    total_docs = Document.objects.filter(user_id=user_id).count()
    total_obs = Observation.objects.filter(user_id=user_id).count()
    
    # Populate categories (simple stats for now)
    obs_types = Observation.objects.filter(user_id=user_id).values('code').distinct()
    categories = []
    for obs_t in obs_types:
        code = obs_t['code']
        # simple count
        cnt = Observation.objects.filter(user_id=user_id, code=code).count()
        categories.append({
            'code': code,
            'label': code.replace('_', ' ').title(),
            'emoji': '📊',
            'count': cnt,
            'status': 'neutral',
            'last_update': None
        })
    profile['categories'] = categories
    
    profile['summary'] = {
        'total_categories': len(categories),
        'total_observations': total_obs,
        'total_documents': total_docs
    }

    return profile


def prioritize_prompts(prompts: List[Dict[str, Any]], max_prompts: int = 10) -> List[Dict[str, Any]]:
    """
    Prioriza prompts basándose en el score asignado.
    """
    # Filtrar elementos inválidos
    valid_prompts = [p for p in prompts if isinstance(p, dict)]
    # Ordenar por score descendente
    valid_prompts.sort(key=lambda x: x.get('score', 0), reverse=True)
    return valid_prompts[:max_prompts]


if __name__ == '__main__':
    # Test con demo-alex
    print("Analizando perfil de demo-alex...")
    # Asumiendo ID 8 para el usuario sintético creado recientemente, o 5 para demo anterior
    try:
        profile = analyze_user_health_profile(8) 
        print(f"\n=== PERFIL DE {profile['username'].upper()} ===")
        print("\n=== PROMPTS INTELIGENTES ===")
        for i, p in enumerate(profile['intelligent_prompts'], 1):
            print(f"\n{i}. {p['emoji']} {p['prompt']}")
            print(f"   [{p['priority'].upper()}] {p['insight']}")
    except Exception as e:
        print(f"Error testing: {e}")
