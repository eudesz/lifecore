from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from apps.api.auth import require_api_key, smart_consent, audit_access
from apps.lifecore.models import Observation
import csv
import io


def _assert_user_scope(request, user_id: str | int):
    if getattr(request, '_platform_system', False):
        return None
    role = getattr(request, '_platform_role', 'patient')
    if role in ('doctor', 'admin'):
        return None
    user = getattr(request, '_platform_user', None)
    try:
        if not user or int(user_id) != int(user.id):
            return JsonResponse({'error': 'Forbidden'}, status=403)
    except Exception:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    return None


def _get_filtered_observations(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return None, JsonResponse({'error': 'user_id is required'}, status=400)
    err = _assert_user_scope(request, user_id)
    if err:
        return None, err
    code = request.GET.get('code')
    since = parse_datetime(request.GET.get('since') or '')
    until = parse_datetime(request.GET.get('until') or '')
    qs = Observation.objects.filter(user_id=user_id)
    if code:
        qs = qs.filter(code=code)
    if since:
        qs = qs.filter(taken_at__gte=since)
    if until:
        qs = qs.filter(taken_at__lte=until)
    return qs.order_by('taken_at'), None


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='reports', purpose='export')
@audit_access(resource='reports', action='observations_csv')
def observations_csv(request):
    qs, err = _get_filtered_observations(request)
    if err:
        return err
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['code', 'value', 'unit', 'taken_at', 'source'])
    for o in qs:
        writer.writerow([o.code, o.value, o.unit, o.taken_at.isoformat(), o.source])
    resp = HttpResponse(buffer.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="observations.csv"'
    return resp


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='reports', purpose='export')
@audit_access(resource='reports', action='summary_markdown')
def summary_markdown(request):
    qs, err = _get_filtered_observations(request)
    if err:
        return err
    counts = {}
    for o in qs:
        counts[o.code] = counts.get(o.code, 0) + 1
    lines = ["# Resumen de observaciones", "", "## Conteo por código:"]
    for code, c in counts.items():
        lines.append(f"- {code}: {c}")
    lines.append("")
    lines.append("## Fuentes registradas:")
    sources = sorted(set(o.source for o in qs))
    for s in sources:
        lines.append(f"- {s}")
    body = "\n".join(lines)
    resp = HttpResponse(body, content_type='text/markdown')
    resp['Content-Disposition'] = 'attachment; filename="summary.md"'
    return resp


@csrf_exempt
@require_http_methods(["GET"])
@require_api_key
@smart_consent(resource='reports', purpose='export')
@audit_access(resource='reports', action='summary_pdf')
def summary_pdf(request):
    qs, err = _get_filtered_observations(request)
    if err:
        return err
    try:
        from reportlab.pdfgen import canvas  # type: ignore
        from reportlab.lib.pagesizes import A4  # type: ignore
    except Exception:
        return JsonResponse({'error': 'PDF export not available. Install reportlab.'}, status=501)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Resumen de observaciones")
    y -= 24

    p.setFont("Helvetica", 10)
    # Conteo por código
    counts = {}
    for o in qs:
        counts[o.code] = counts.get(o.code, 0) + 1
    p.drawString(40, y, "Conteo por código:")
    y -= 16
    for code, c in sorted(counts.items()):
        p.drawString(52, y, f"- {code}: {c}")
        y -= 14
        if y < 60:
            p.showPage(); y = height - 40

    # Fuentes
    y -= 8
    p.drawString(40, y, "Fuentes registradas:")
    y -= 16
    for s in sorted(set(o.source for o in qs)):
        p.drawString(52, y, f"- {s}")
        y -= 14
        if y < 60:
            p.showPage(); y = height - 40

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()

    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="summary.pdf"'
    return resp
