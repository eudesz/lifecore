# Scaffold de rutas (documentación). Integrar en Django urls.py del proyecto.

ROUTES = [
    {
        'method': 'POST',
        'path': '/api/agents/v2/analyze',
        'handler': 'apps.agents_v2.views.analyze',
        'flags': ['FEATURE_AGENTS_V2']
    },
    {
        'method': 'GET',
        'path': '/api/rag/embedding-status',
        'handler': 'apps.lifecore.views.embedding_status',
        'flags': ['FEATURE_AGENTS_V2']
    },
    {
        'method': 'POST',
        'path': '/api/lifecore/mood',
        'handler': 'apps.lifecore.views.mood_create',
        'flags': ['FEATURE_LIFECORE']
    },
    {
        'method': 'GET',
        'path': '/api/lifecore/mood',
        'handler': 'apps.lifecore.views.mood_list',
        'flags': ['FEATURE_LIFECORE']
    },
    {
        'method': 'GET',
        'path': '/api/prompts/intelligent',
        'handler': 'apps.lifecore.views.prompts_intelligent',
        'flags': ['FEATURE_AGENTS_V2']
    },
    {
        'method': 'GET',
        'path': '/api/agents/v2/status',
        'handler': 'apps.agents_v2.views.status',
        'flags': ['FEATURE_AGENTS_V2']
    },
    {
        'method': 'POST',
        'path': '/api/lifecore/observations',
        'handler': 'apps.lifecore.views.observations_create',
        'flags': ['FEATURE_LIFECORE']
    },
    {
        'method': 'GET',
        'path': '/api/lifecore/timeline',
        'handler': 'apps.lifecore.views.timeline_list',
        'flags': ['FEATURE_LIFECORE']
    },
    {
        'method': 'POST',
        'path': '/api/doctor-link',
        'handler': 'apps.lifecore.views.doctor_link_create',
        'flags': ['FEATURE_LIFECORE']
    },
    {
        'method': 'GET',
        'path': '/d/:token',
        'handler': 'apps.lifecore.views.doctor_link_view',
        'flags': ['FEATURE_LIFECORE']
    },
]
