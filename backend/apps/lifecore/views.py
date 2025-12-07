from datetime import datetime, timedelta
from typing import Any, Dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
import json

from .models import Observation, TimelineEvent, DoctorShareLink, AuditLog, ConsentPolicy, ApiClientToken, Document, DocumentChunk, MemoryEpisode, MemorySemantic
from .serializers import ObservationSerializer, TimelineEventSerializer, DoctorShareLinkSerializer, ConsentPolicySerializer, DocumentSerializer
from apps.api.auth import require_api_key, audit_access, smart_consent
from .embedding import chunk_text, text_to_embedding, cosine_similarity
from .vectorstore_faiss import FaissVectorStore
from .intelligent_prompts import analyze_user_health_profile
from .treatment_models import Treatment, TreatmentLog, TreatmentProgress
from .models import Condition, EventCondition

User = get_user_model()


def _assert_user_scope(request, user_id: str | int) -> JsonResponse | None:
    if getattr(request, '_platform_system', False):
        return None
    role = getattr(request, '_platform_role', 'patient')
    if role in ('doctor', 'admin'):
        return None
    user = getattr(request, '_platform_user', None)
    if not user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        if int(user_id) != int(user.id):
            return JsonResponse({'error': 'Forbidden'}, status=403)
    except Exception:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    return None


def _index_document(doc: Document):
    DocumentChunk.objects.filter(document=doc).delete()
    parts = chunk_text(doc.content or '')
    for i, part in enumerate(parts):
        emb = text_to_embedding(part)
        DocumentChunk.objects.create(user=doc.user, document=doc, chunk_index=i, text=part, embedding=emb)


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='observations', purpose='write')
@audit_access(resource='observations', action='create')
def observations_create(request):
    data = json.loads(request.body or '{}')
    if data.get('user') is None:
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, data.get('user'))
    if scope_err:
        return scope_err
    serializer = ObservationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='observations', purpose='analysis')
@audit_access(resource='observations', action='list')
def observations_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    code = request.GET.get('code')
    since_str = request.GET.get('since')
    until_str = request.GET.get('until')
    qs = Observation.objects.filter(user_id=user_id)
    if code:
        qs = qs.filter(code=code)
    if since_str:
        dt = parse_datetime(since_str)
        if dt:
            qs = qs.filter(taken_at__gte=dt)
    if until_str:
        dt = parse_datetime(until_str)
        if dt:
            qs = qs.filter(taken_at__lte=dt)
    qs = qs.order_by('taken_at')
    data = ObservationSerializer(qs, many=True).data
    return JsonResponse({'observations': data})


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='documents', purpose='write')
@audit_access(resource='documents', action='create')
def documents_create(request):
    data = json.loads(request.body or '{}')
    if not data.get('user'):
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, data.get('user'))
    if scope_err:
        return scope_err
    serializer = DocumentSerializer(data=data)
    if serializer.is_valid():
        doc = serializer.save()
        try:
            _index_document(doc)
        except Exception:
            pass
        return JsonResponse(DocumentSerializer(doc).data, status=201)
    return JsonResponse(serializer.errors, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='documents', purpose='write')
@audit_access(resource='documents', action='reindex')
def documents_reindex(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user_id') or data.get('user')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    doc_id = data.get('document_id')
    use_faiss = bool(data.get('use_faiss', False))
    if doc_id:
        try:
            doc = Document.objects.get(id=doc_id, user_id=user_id)
        except Document.DoesNotExist:
            return JsonResponse({'error': 'document not found'}, status=404)
        _index_document(doc)
        if use_faiss and FaissVectorStore.is_available():
            try:
                FaissVectorStore(doc.user_id).build()
            except Exception:
                pass
        return JsonResponse({'status': 'ok', 'indexed': 1, 'faiss': use_faiss})
    docs = Document.objects.filter(user_id=user_id)
    count = 0
    last_user_id = None
    for d in docs:
        _index_document(d)
        count += 1
        last_user_id = d.user_id
    if use_faiss and last_user_id and FaissVectorStore.is_available():
        try:
            FaissVectorStore(int(last_user_id)).build()
        except Exception:
            pass
    return JsonResponse({'status': 'ok', 'indexed': count, 'faiss': use_faiss})


@csrf_exempt
@require_http_methods(["GET"])
def embedding_status(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    store = FaissVectorStore(int(user_id))
    idx_exists = os.path.exists(store.index_path)
    meta_exists = os.path.exists(store.meta_path)
    return JsonResponse({
        'faiss_available': FaissVectorStore.is_available(),
        'index_exists': bool(idx_exists and meta_exists),
        'index_path': store.index_path,
    })


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='memory', purpose='analysis')
@audit_access(resource='memory', action='summarize')
def memory_summarize(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user_id') or data.get('user')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    days = int(data.get('days', 7))
    since = datetime.utcnow() - timedelta(days=days)
    episodes = MemoryEpisode.objects.filter(user_id=user_id, occurred_at__gte=since).order_by('-occurred_at')[:200]
    if not episodes:
        return JsonResponse({'status': 'ok', 'summary': 'Sin episodios para resumir.'})
    # Resumen simple: primeras líneas + conteos
    texts = [e.content for e in episodes if e.content]
    snippet = (' '.join(texts))[:800]
    summary = f"Resumen últimos {days} días: {snippet}"
    MemorySemantic.objects.update_or_create(
        user_id=user_id,
        key='chat_summary',
        defaults={'value': {'days': days, 'generated_at': datetime.utcnow().isoformat(), 'summary': summary}},
    )
    TimelineEvent.objects.create(user_id=user_id, kind='memory.summary', payload={'days': days}, occurred_at=datetime.utcnow())
    return JsonResponse({'status': 'ok', 'summary': summary})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='documents', purpose='analysis')
@audit_access(resource='documents', action='list')
def documents_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    qs = Document.objects.filter(user_id=user_id).order_by('-created_at')
    data = DocumentSerializer(qs, many=True).data
    return JsonResponse({'documents': data})


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='observations', purpose='write')
@audit_access(resource='observations', action='create_mood')
def mood_create(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user') or data.get('user_id')
    if user_id is None:
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    try:
        score = float(data.get('score'))
    except Exception:
        return JsonResponse({'error': 'score is required (0-10)'}, status=400)
    note = (data.get('note') or '').strip()
    ts = data.get('taken_at')
    dt = parse_datetime(ts) if ts else datetime.utcnow()
    obs = Observation.objects.create(
        user_id=user_id,
        code='mood',
        value=score,
        unit='',
        taken_at=dt,
        source='user_checkin',
        extra={'note': note} if note else {},
    )
    TimelineEvent.objects.create(user_id=user_id, kind='checkin.mood', payload={'score': score}, occurred_at=datetime.utcnow())
    return JsonResponse({'status': 'created', 'id': obs.id})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='observations', purpose='analysis')
@audit_access(resource='observations', action='list_mood')
def mood_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    days = int(request.GET.get('days', '30'))
    since = datetime.utcnow() - timedelta(days=days)
    qs = Observation.objects.filter(user_id=user_id, code='mood', taken_at__gte=since).order_by('taken_at')
    data = [
        {
            'taken_at': o.taken_at.isoformat(),
            'score': o.value,
            'note': (o.extra or {}).get('note')
        } for o in qs
    ]
    return JsonResponse({'mood': data})

@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='timeline', purpose='analysis')
@audit_access(resource='timeline', action='list')
def timeline_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    days = int(request.GET.get('days', '90'))
    since = datetime.utcnow() - timedelta(days=days)
    events = TimelineEvent.objects.filter(user_id=user_id, occurred_at__gte=since).order_by('-occurred_at')[:200]
    data = TimelineEventSerializer(events, many=True).data
    return JsonResponse({'events': data})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='timeline', purpose='analysis')
@audit_access(resource='timeline', action='advanced')
def timeline_advanced(request):
    """
    Timeline avanzada con filtros y enriquecimiento de datos.
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    categories = [c for c in (request.GET.get('categories') or '').split(',') if c]
    conditions = [c for c in (request.GET.get('conditions') or '').split(',') if c]
    severity = request.GET.get('severity')

    # Fetch TimelineEvents
    qs = TimelineEvent.objects.filter(user_id=user_id)
    if date_from:
        qs = qs.filter(occurred_at__gte=date_from)
    if date_to:
        qs = qs.filter(occurred_at__lte=date_to)
    if categories:
        qs = qs.filter(category__in=categories)
    if conditions:
        # prefer normalized linking when available
        cond_ids = list(Condition.objects.filter(slug__in=conditions).values_list('id', flat=True))
        if cond_ids:
            qs = qs.filter(conditions_link__condition_id__in=cond_ids)
        else:
            qs = qs.filter(related_conditions__overlap=conditions)
    if severity:
        qs = qs.filter(severity__in=['high', 'critical'] if severity == 'high' else [severity])

    # Fetch Documents (mapped to events)
    doc_qs = Document.objects.filter(user_id=user_id)
    if date_from:
        doc_qs = doc_qs.filter(created_at__gte=date_from)
    if date_to:
        doc_qs = doc_qs.filter(created_at__lte=date_to)
    
    # Fetch Treatments (mapped to events)
    tx_qs = Treatment.objects.filter(user_id=user_id)
    if date_from:
        tx_qs = tx_qs.filter(start_date__gte=date_from)
    if date_to:
        tx_qs = tx_qs.filter(start_date__lte=date_to)

    events_out = []
    
    # Process TimelineEvents
    for e in qs.order_by('occurred_at').distinct()[:1000]:
        # Métricas cercanas (últimos 7 días alrededor del evento)
        start_win = e.occurred_at - timedelta(days=7)
        end_win = e.occurred_at + timedelta(days=7)
        metrics = {}
        try:
            near_glucose = Observation.objects.filter(user_id=user_id, code='glucose', taken_at__range=(start_win, end_win)).order_by('-taken_at').first()
            if near_glucose:
                metrics['glucose'] = float(near_glucose.value)
            near_bp = Observation.objects.filter(user_id=user_id, code='blood_pressure_systolic', taken_at__range=(start_win, end_win)).order_by('-taken_at').first()
            if near_bp:
                metrics['bp_sys'] = float(near_bp.value)
            near_weight = Observation.objects.filter(user_id=user_id, code='weight', taken_at__range=(start_win, end_win)).order_by('-taken_at').first()
            if near_weight:
                metrics['weight'] = float(near_weight.value)
        except Exception:
            metrics = {}

        payload = e.payload or {}
        # Prefer explicit title from payload; otherwise derive a human‑friendly label
        title = payload.get('title')
        if not title:
            if e.kind == 'agents_v2.analyze':
                # Show the agent category and a snippet of the query instead of a raw kind string
                cat = (payload.get('category') or 'general').replace('_', ' ').title()
                q = (payload.get('query') or '').strip()
                if q:
                    snippet = q[:80] + ('…' if len(q) > 80 else '')
                    title = f'Agent analysis — {cat}: {snippet}'
                else:
                    title = f'Agent analysis — {cat}'
            else:
                title = e.kind.replace('.', ' ').title()

        events_out.append({
            'id': e.id,
            'date': e.occurred_at.isoformat(),
            'kind': e.kind,
            'category': e.category,
            'severity': e.severity,
            'title': title,
            'description': payload.get('description') or '',
            'metrics': metrics,
            'related_conditions': e.related_conditions,
            'document_id': e.data_summary.get('source_doc_id') if e.data_summary else None,
        })

    # Process Documents -> Events
    if not categories or 'lab' in categories or 'consultation' in categories:
        for d in doc_qs[:500]:
            cat = 'lab' if 'report' in d.title.lower() or '.pdf' in d.title.lower() else 'consultation'
            if categories and cat not in categories:
                continue
            
            events_out.append({
                'id': f'doc_{d.id}',
                'date': d.created_at.isoformat(),
                'kind': 'document.created',
                'category': cat,
                'severity': 'info',
                'title': d.title,
                'description': (d.content or '')[:200] + '...',
                'metrics': {},
                'related_conditions': [],
            })

    # Process Treatments -> Events
    if not categories or 'treatment' in categories:
        for t in tx_qs[:500]:
            events_out.append({
                'id': f'tx_{t.id}',
                'date': t.start_date.isoformat(),
                'kind': 'treatment.start',
                'category': 'treatment',
                'severity': 'info',
                'title': f"Inicio: {t.name}",
                'description': f"{t.medication_type} - {t.dosage} {t.frequency}. Estado: {t.status}",
                'metrics': {},
                'related_conditions': [t.condition] if t.condition else [],
            })

    # Sort all events by date
    events_out.sort(key=lambda x: x['date'])


    # Hierarchical grouping by condition then category
    cond_slugs = conditions or []
    cond_objs = list(Condition.objects.filter(slug__in=cond_slugs)) if cond_slugs else list(Condition.objects.all())
    cond_map = {c.id: {'slug': c.slug, 'name': c.name, 'color': c.color} for c in cond_objs}
    cond_groups: Dict[str, Dict[str, Any]] = {}
    # Build a helper map event_id -> condition slugs
    ev_to_cond = {}
    # Fix: Filter only integer IDs for EventCondition query (real TimelineEvents)
    real_event_ids = [e['id'] for e in events_out if isinstance(e['id'], int)]
    link_qs = EventCondition.objects.filter(event_id__in=real_event_ids).select_related('condition')
    for l in link_qs:
        ev_to_cond.setdefault(l.event_id, []).append(l.condition.slug)
    # Ensure events expose normalized condition slugs so frontend grouping/filter works
    for ev in events_out:
        slugs = ev_to_cond.get(ev['id'])
        if slugs:
            ev['related_conditions'] = slugs
    for ev in events_out:
        slugs = ev_to_cond.get(ev['id']) or (ev.get('related_conditions') or ['general'])
        for slug in slugs:
            key = slug
            if key not in cond_groups:
                cond_groups[key] = {'condition': cond_map.get(next((cid for cid, c in cond_map.items() if c['slug']==slug), None), {'slug': slug, 'name': slug.title(), 'color': '#64748b'}), 'lanes': {}}
            lane = cond_groups[key]['lanes'].setdefault(ev['category'], [])
            lane.append(ev)

    conditions_payload = []
    for slug, grp in cond_groups.items():
        lanes = [{'category': cat, 'events': arr} for cat, arr in grp['lanes'].items()]
        conditions_payload.append({'condition': grp['condition'], 'lanes': lanes})

    return JsonResponse({'events': events_out, 'conditions': conditions_payload, 'total': len(events_out)})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='conditions', purpose='analysis')
@audit_access(resource='conditions', action='list')
def conditions_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    # counts by Condition through EventCondition
    counts = {}
    link_qs = EventCondition.objects.filter(event__user_id=user_id).values('condition_id')
    for row in link_qs:
        cid = row['condition_id']
        counts[cid] = counts.get(cid, 0) + 1
    payload = []
    for c in Condition.objects.all():
        payload.append({'slug': c.slug, 'name': c.name, 'color': c.color, 'count': counts.get(c.id, 0)})
    return JsonResponse({'conditions': payload})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='treatments', purpose='analysis')
@audit_access(resource='treatments', action='list')
def treatments_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err

    qs = Treatment.objects.filter(user_id=user_id).order_by('-start_date')
    data = []
    for t in qs[:500]:
        data.append({
            'id': t.id,
            'name': t.name,
            'condition': t.condition,
            'dosage': t.dosage,
            'frequency': t.frequency,
            'status': t.status,
            'start_date': t.start_date.isoformat(),
            'end_date': t.end_date.isoformat() if t.end_date else None,
        })
    return JsonResponse({'treatments': data})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='treatments', purpose='analysis')
@audit_access(resource='treatments', action='adherence')
def treatments_adherence(request):
    """
    Cálculo simple de adherencia últimos N días sumando logs tomados/scheduled.
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    days = int(request.GET.get('days', '30'))
    since = datetime.utcnow() - timedelta(days=days)
    scheduled = 0
    taken = 0
    logs = TreatmentLog.objects.filter(treatment__user_id=user_id, scheduled_date__gte=since)
    for log in logs:
        scheduled += 1
        if log.taken:
            taken += 1
    pct = round((taken / scheduled) * 100.0, 1) if scheduled else 0.0
    return JsonResponse({'scheduled': scheduled, 'taken': taken, 'adherence_pct': pct, 'days': days})

@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='doctor_link', purpose='sharing')
@audit_access(resource='doctor_link', action='create')
def doctor_link_create(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user')
    if not user_id:
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    expires_in_days = int(data.get('expires_in_days', 7))
    scope_meta = {
        'conditions': data.get('conditions') or [],
        'categories': data.get('categories') or [],
        'date_from': data.get('date_from'),
        'date_to': data.get('date_to'),
    }
    link = DoctorShareLink.objects.create(
        user_id=user_id,
        expires_at=timezone.now() + timedelta(days=expires_in_days),
        scope='chat',
        scope_meta=scope_meta,
    )
    return JsonResponse(DoctorShareLinkSerializer(link).data, status=201)

@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='doctor_link', purpose='sharing')
@audit_access(resource='doctor_link', action='list')
def doctor_links_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    qs = DoctorShareLink.objects.filter(user_id=user_id).order_by('-created_at')[:200]
    data = [
        {
            'id': l.id,
            'token': l.token,
            'scope': l.scope,
            'revoked': l.revoked,
            'created_at': l.created_at.isoformat(),
            'expires_at': l.expires_at.isoformat() if l.expires_at else None,
            'url': f"/doctor/{l.token}",
        }
        for l in qs
    ]
    return JsonResponse({'links': data})

@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@smart_consent(resource='doctor_link', purpose='sharing')
@audit_access(resource='doctor_link', action='revoke')
def doctor_links_revoke(request):
    try:
        data = json.loads(request.body or '{}')
    except Exception:
        data = {}
    token = data.get('token')
    link_id = data.get('id')
    if not token and not link_id:
        return JsonResponse({'error': 'token or id is required'}, status=400)
    try:
        link = DoctorShareLink.objects.get(token=token) if token else DoctorShareLink.objects.get(id=link_id)
    except DoctorShareLink.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)
    scope_err = _assert_user_scope(request, link.user_id)
    if scope_err:
        return scope_err
    link.revoked = True
    link.save(update_fields=['revoked'])
    return JsonResponse({'status': 'revoked'})

@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='doctor_link', purpose='audit')
@audit_access(resource='doctor_link', action='audit')
def doctor_links_audit(request):
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    qs = MemoryEpisode.objects.filter(user_id=user_id, kind='chat')
    if token:
        qs = qs.filter(metadata__doctor_token=token)
    qs = qs.order_by('-occurred_at')[:200]
    out = []
    for e in qs:
        meta = e.metadata or {}
        if meta.get('doctor_token'):
            out.append({
                'occurred_at': e.occurred_at.isoformat(),
                'role': meta.get('role', 'assistant'),
                'text': e.content,
                'scope': meta.get('conversation_scope') or {},
                'token': meta.get('doctor_token'),
            })
    return JsonResponse({'entries': out})

@csrf_exempt
@require_http_methods(["GET"])
@audit_access(resource='doctor_link', action='view_public')
def doctor_link_view(request, token: str):
    try:
        link = DoctorShareLink.objects.get(token=token, revoked=False)
        if link.expires_at and link.expires_at < timezone.now():
            return JsonResponse({'error': 'Link expired'}, status=410)
        latest_obs = Observation.objects.filter(user=link.user).order_by('-taken_at')[:50]
        # Serialización ligera y robusta sin DRF para evitar fallos
        obs_data = [
            {
                'code': o.code,
                'value': float(o.value),
                'unit': o.unit,
                'taken_at': (o.taken_at.isoformat() if hasattr(o.taken_at, 'isoformat') else str(o.taken_at)),
                'source': o.source,
            }
            for o in latest_obs
        ]
        return JsonResponse({'user': link.user_id, 'latest_observations': obs_data})
    except DoctorShareLink.DoesNotExist:
        return JsonResponse({'error': 'Invalid link'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Server error', 'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def doctor_chat_view(request, token: str):
    """
    Vista pública (token) para que el médico vea el historial de conversación.
    Solo lectura; expira según el token.
    """
    try:
        link = DoctorShareLink.objects.get(token=token, revoked=False)
        if link.expires_at and link.expires_at < timezone.now():
            return JsonResponse({'error': 'Link expired'}, status=410)
        # Últimos 100 turnos de chat en orden cronológico, SOLO los del médico (vía token) y respuestas asociadas
        episodes = list(
            MemoryEpisode.objects.filter(user_id=link.user_id, kind='chat')
            .order_by('-occurred_at')[:100]
        )
        out = []
        for e in reversed(episodes):
            meta = e.metadata or {}
            token_meta = meta.get('doctor_token')
            role = meta.get('role', 'assistant')
            # Sólo exponer mensajes asociados al token actual
            if token_meta == token and role in ('doctor', 'assistant_doctor'):
                out.append({
                    'occurred_at': e.occurred_at.isoformat(),
                    'role': 'assistant' if role == 'assistant_doctor' else role,
                    'text': e.content,
                })
        return JsonResponse({'user': link.user_id, 'conversation': out})
    except DoctorShareLink.DoesNotExist:
        return JsonResponse({'error': 'Invalid link'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def doctor_chat_ask(request, token: str):
    """
    Endpoint público para que el médico haga consultas conversacionales
    usando el token del paciente. Solo lectura; no modifica datos del paciente.
    """
    from apps.agents_v2 import views as agents_views
    try:
        link = DoctorShareLink.objects.get(token=token, revoked=False)
        if link.expires_at and link.expires_at < timezone.now():
            return JsonResponse({'error': 'Link expired'}, status=410)
    except DoctorShareLink.DoesNotExist:
        return JsonResponse({'error': 'Invalid link'}, status=404)
    try:
        body = json.loads(request.body or '{}')
    except Exception:
        body = {}
    query = (body or {}).get('query') or ''
    conversation_id = (body or {}).get('conversation_id')
    # Marcar el request como de rol doctor para metadatos y auditoría
    setattr(request, '_platform_system', True)
    setattr(request, '_platform_role', 'doctor')
    payload = {
        'query': query,
        'user_id': link.user_id,
        'doctor_token': token,
        'context_filters': link.scope_meta or {},
    }
    if conversation_id:
        payload['conversation_id'] = conversation_id
    resp = agents_views.analyze(payload, request=request)
    return JsonResponse(resp)


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@audit_access(resource='consent', action='list')
def consent_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    qs = ConsentPolicy.objects.filter(user_id=user_id).order_by('resource', 'purpose')
    data = ConsentPolicySerializer(qs, many=True).data
    return JsonResponse({'consents': data})


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@audit_access(resource='consent', action='upsert')
def consent_upsert(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user')
    if not user_id:
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    resource = data.get('resource')
    purpose = data.get('purpose')
    if not resource or not purpose:
        return JsonResponse({'error': 'resource and purpose are required'}, status=400)
    obj, created = ConsentPolicy.objects.get_or_create(user_id=user_id, resource=resource, purpose=purpose)
    obj.allowed = bool(data.get('allowed', True))
    if 'scope' in data:
        obj.scope = data.get('scope') or obj.scope
    expires_at = data.get('expires_at')
    if expires_at:
        dt = parse_datetime(expires_at)
        if dt:
            obj.expires_at = dt
    obj.save()
    return JsonResponse(ConsentPolicySerializer(obj).data, status=201 if created else 200)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
@require_api_key
@audit_access(resource='consent', action='delete')
def consent_delete(request):
    try:
        data = json.loads(request.body or '{}') if request.method != 'GET' else {}
    except Exception:
        data = {}
    obj_id = data.get('id')
    user_id = data.get('user')
    if obj_id:
        try:
            obj = ConsentPolicy.objects.get(id=obj_id)
        except ConsentPolicy.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)
        scope_err = _assert_user_scope(request, obj.user_id)
        if scope_err:
            return scope_err
        obj.delete()
        return JsonResponse({'status': 'deleted'})
    if not user_id:
        return JsonResponse({'error': 'id or (user, resource, purpose) required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    resource = data.get('resource')
    purpose = data.get('purpose')
    if not resource or not purpose:
        return JsonResponse({'error': 'resource and purpose are required'}, status=400)
    ConsentPolicy.objects.filter(user_id=user_id, resource=resource, purpose=purpose).delete()
    return JsonResponse({'status': 'deleted'})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@audit_access(resource='tokens', action='list')
def tokens_list(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    qs = ApiClientToken.objects.filter(user_id=user_id).order_by('-created_at')
    data = [
        {
            'id': t.id,
            'user': t.user_id,
            'role': t.role,
            'token': t.token,
            'active': t.active,
            'expires_at': t.expires_at.isoformat() if t.expires_at else None,
            'created_at': t.created_at.isoformat(),
        }
        for t in qs
    ]
    return JsonResponse({'tokens': data})


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@audit_access(resource='tokens', action='create')
def tokens_create(request):
    data = json.loads(request.body or '{}')
    user_id = data.get('user')
    if not user_id:
        return JsonResponse({'error': 'user is required'}, status=400)
    scope_err = _assert_user_scope(request, user_id)
    if scope_err:
        return scope_err
    role = data.get('role') or 'patient'
    expires_at = data.get('expires_at')
    obj = ApiClientToken.objects.create(user_id=user_id, role=role)
    if expires_at:
        dt = parse_datetime(expires_at)
        if dt:
            obj.expires_at = dt
            obj.save()
    return JsonResponse({
        'id': obj.id,
        'user': obj.user_id,
        'role': obj.role,
        'token': obj.token,
        'active': obj.active,
        'expires_at': obj.expires_at.isoformat() if obj.expires_at else None,
        'created_at': obj.created_at.isoformat(),
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
@audit_access(resource='tokens', action='update')
def tokens_update(request):
    data = json.loads(request.body or '{}')
    obj_id = data.get('id')
    if not obj_id:
        return JsonResponse({'error': 'id is required'}, status=400)
    try:
        obj = ApiClientToken.objects.get(id=obj_id)
    except ApiClientToken.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)
    scope_err = _assert_user_scope(request, obj.user_id)
    if scope_err:
        return scope_err
    if 'active' in data:
        obj.active = bool(data.get('active'))
    if 'role' in data and data.get('role') in ('patient', 'doctor', 'admin'):
        obj.role = data.get('role')
    if 'expires_at' in data:
        dt = parse_datetime(data.get('expires_at') or '')
        obj.expires_at = dt if dt else None
    obj.save()
    return JsonResponse({'status': 'updated'})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@audit_access(resource='audit', action='list')
def audit_list(request):
    role = getattr(request, '_platform_role', 'patient')
    if role != 'admin' and not getattr(request, '_platform_system', False):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    limit = int(request.GET.get('limit', '100'))
    logs = AuditLog.objects.order_by('-created_at')[:max(1, min(limit, 500))]
    data = [
        {
            'created_at': a.created_at.isoformat(),
            'user': a.user_id,
            'actor_role': a.actor_role,
            'resource': a.resource,
            'action': a.action,
            'success': a.success,
            'status_code': a.status_code,
            'method': a.method,
            'path': a.path,
            'ip': a.ip,
        }
        for a in logs
    ]
    return JsonResponse({'logs': data})


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='observations', purpose='read')
@audit_access(resource='prompts', action='intelligent')
def prompts_intelligent(request):
    """
    Endpoint para obtener prompts inteligentes personalizados.
    
    GET /api/prompts/intelligent?user_id=X
    
    Response:
    {
        "user_id": 5,
        "username": "demo-alex",
        "categories": [
            {
                "code": "glucose",
                "emoji": "🩸",
                "label": "Glucosa",
                "count": 30,
                "status": "neutral",
                "last_update": "2025-11-07T12:00:00Z"
            },
            ...
        ],
        "intelligent_prompts": [
            {
                "prompt": "¿Cómo ha evolucionado mi glucosa en los últimos 30 días?",
                "category": "glucose",
                "type": "temporal",
                "priority": "medium",
                "emoji": "🩸",
                "insight": "Promedio: 124.1 mg/dL",
                "score": 0.8
            },
            ...
        ],
        "summary": {
            "total_categories": 6,
            "total_observations": 102,
            "total_documents": 163
        }
    }
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)
    
    # Verificar permisos
    err = _assert_user_scope(request, user_id)
    if err:
        return err
    
    try:
        user_id_int = int(user_id)
        
        # Generar perfil con prompts inteligentes
        try:
            profile = analyze_user_health_profile(user_id_int)
        except Exception as inner_e:
            print(f"Error generating prompts: {inner_e}")
            # Fallback profile
            user = User.objects.get(id=user_id_int)
            profile = {
                'user_id': user_id_int,
                'username': user.username,
                'categories': [],
                'intelligent_prompts': [],
                'summary': {'total_categories': 0, 'total_observations': 0, 'total_documents': 0}
            }
        
        return JsonResponse({
            'user_id': profile['user_id'],
            'username': profile['username'],
            'categories': profile['categories'],
            'intelligent_prompts': profile['intelligent_prompts'],
            'summary': profile['summary']
        })
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid user_id'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

