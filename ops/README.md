# Operación y Despliegue

## Variables de entorno

Backend (Django):
- DJANGO_SECRET_KEY (secret)
- DJANGO_API_KEY (secret)
- DATABASE_URL (secret) p.ej. `postgres://user:pass@host:5432/dbname`
- DB_SSL_REQUIRE=true|false (si la DB requiere SSL)
- DJANGO_DEBUG=false (prod)
- SECURE_SSL_REDIRECT=true
- FEATURE_RAG=true|false
- FEATURE_PROACTIVITY=true|false
- SENTRY_DSN (opcional)

Frontend (Next.js):
- NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN (URL del backend)
- NEXT_PUBLIC_PLATFORM_API_KEY (clave de sistema para pruebas)

## Docker/Compose

- Compose local disponible (`platform/docker-compose.yml`). Útil para desarrollo.

## Helm (Kubernetes)

Ruta del chart: `platform/ops/helm/platform`

Valores rápidos:
- `backend.image.repository` / `backend.image.tag`
- `frontend.image.repository` / `frontend.image.tag`
- `backend.secret.DJANGO_SECRET_KEY` / `backend.secret.DJANGO_API_KEY`
- `backend.secret.DATABASE_URL` / `backend.env.DB_SSL_REQUIRE`
- `ingress.enabled`, `ingress.hosts.frontend.host`, `ingress.hosts.backend.host`

Instalación (namespace `platform`):

```bash
helm upgrade --install platform platform/ops/helm/platform \
  -n platform --create-namespace \
  --set backend.image.repository=REPO/backend --set backend.image.tag=TAG \
  --set frontend.image.repository=REPO/frontend --set frontend.image.tag=TAG \
  --set backend.secret.DJANGO_SECRET_KEY=CHANGE_ME \
  --set backend.secret.DJANGO_API_KEY=SET_YOUR_KEY \
  --set backend.secret.DATABASE_URL="postgres://user:pass@host:5432/db"
```

Comprobación:
```bash
kubectl -n platform get pods,svc,ingress
kubectl -n platform logs deploy/platform-backend -f
```

Habilitar Ingress (opcional):
```bash
helm upgrade --install platform platform/ops/helm/platform \
  -n platform --create-namespace \
  --set ingress.enabled=true \
  --set ingress.hosts.frontend.host=app.example.com \
  --set ingress.hosts.backend.host=api.example.com
```

## Runbook de operación

- Salud:
  - Backend: `/api/agents/v2/status` (readiness), `/api/metrics` (liveness)
  - Frontend: `/` responde 200
- Flags:
  - `/api/flags` lista `RAG` y `PROACTIVITY`
  - Cambiar en despliegue vía `FEATURE_RAG/FEATURE_PROACTIVITY`.
- Logs:
  - `kubectl logs deploy/platform-backend -n platform -f`
- Rotación de claves:
  - Actualizar `platform-secrets` (Helm values) y `helm upgrade`
- Errores:
  - Ver Sentry si `SENTRY_DSN` configurado
- Migraciones/estáticos:
  - Se ejecutan en `initContainer` del backend en cada despliegue (`migrate` + `collectstatic`)
- Proactividad:
  - CronJob `platform-proactivity` corre cada 6 horas

## Seguridad
- Exponer backend solo vía Ingress con TLS
- Rotar `DJANGO_API_KEY` y usar `ApiClientToken` por usuario
- Revisar `RateLimitMiddleware` y cabeceras CSP en producción
