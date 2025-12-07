from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# lightweight handlers to call our scaffold functions without full DRF wiring
from apps.agents_v2 import views as agents_views
from apps.lifecore import views as lifecore_views
from apps.api import reports as reports_views
from apps.api.auth import require_api_key
from apps.api import session as session_views
from apps.api.metrics import metrics_view
from apps.api.flags import flags_view


@csrf_exempt
def agents_analyze_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    import json
    try:
        payload = json.loads(request.body or '{}')
    except Exception:
        payload = {}
    return JsonResponse(agents_views.analyze(payload, request=request))


@require_api_key
@csrf_exempt
def agents_analyze_secure(request):
    return agents_analyze_view(request)


def agents_status_view(request):
    return JsonResponse(agents_views.status())


@csrf_exempt
def mood_view(request):
    if request.method == 'POST':
        return lifecore_views.mood_create(request)
    if request.method == 'GET':
        return lifecore_views.mood_list(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/agents/v2/analyze', agents_analyze_secure),
    path('api/agents/v2/status', agents_status_view),
    path('api/auth/login', session_views.login_view),
    path('api/auth/logout', session_views.logout_view),
    path('api/users/list', session_views.users_list),
    path('api/metrics', metrics_view),
    path('api/flags', flags_view),
    path('api/rag/embedding-status', lifecore_views.embedding_status),
    path('api/prompts/intelligent', lifecore_views.prompts_intelligent),  # GET
    path('api/lifecore/observations', lifecore_views.observations_create),  # POST
    path('api/lifecore/observations/list', lifecore_views.observations_list),  # GET
    path('api/lifecore/documents', lifecore_views.documents_create),  # POST
    path('api/lifecore/documents/list', lifecore_views.documents_list),  # GET
    path('api/lifecore/documents/reindex', lifecore_views.documents_reindex),  # POST
    path('api/lifecore/memory/summarize', lifecore_views.memory_summarize),  # POST
    path('api/lifecore/mood', mood_view),  # GET/POST
    path('api/lifecore/timeline', lifecore_views.timeline_list),
    path('api/lifecore/timeline/advanced', lifecore_views.timeline_advanced),
    path('api/lifecore/treatments/list', lifecore_views.treatments_list),
    path('api/lifecore/treatments/adherence', lifecore_views.treatments_adherence),
    path('api/lifecore/conditions/list', lifecore_views.conditions_list),  # GET
    path('api/lifecore/doctor-links', lifecore_views.doctor_links_list),  # GET
    path('api/lifecore/doctor-links/revoke', lifecore_views.doctor_links_revoke),  # POST
    path('api/lifecore/doctor-links/audit', lifecore_views.doctor_links_audit),  # GET
    path('api/doctor-link', lifecore_views.doctor_link_create),  # POST (crear link público para médico)
    path('api/lifecore/audit', lifecore_views.audit_list),
    path('api/lifecore/consent/list', lifecore_views.consent_list),  # GET
    path('api/lifecore/consent/upsert', lifecore_views.consent_upsert),  # POST
    path('api/lifecore/consent/delete', lifecore_views.consent_delete),  # POST/DELETE
    path('api/lifecore/tokens/list', lifecore_views.tokens_list),  # GET
    path('api/lifecore/tokens/create', lifecore_views.tokens_create),  # POST
    path('api/lifecore/tokens/update', lifecore_views.tokens_update),  # POST
    path('api/reports/observations.csv', reports_views.observations_csv),
    path('api/reports/summary.md', reports_views.summary_markdown),
    path('api/reports/summary.pdf', reports_views.summary_pdf),
    path('d/<str:token>', lifecore_views.doctor_link_view),
    path('d/chat/<str:token>', lifecore_views.doctor_chat_view),
    path('d/ask/<str:token>', lifecore_views.doctor_chat_ask),
]
