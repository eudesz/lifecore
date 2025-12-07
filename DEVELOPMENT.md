# Desarrollo — Plataforma LifeCore

## Backend

1. Instalar dependencias:
   - `pip install -r platform/backend/requirements.txt`
2. Variables de entorno:
   - `DJANGO_SECRET_KEY=...`
   - `DJANGO_API_KEY=dev-secret-key` (clave de sistema para endpoints protegidos)
3. Migraciones:
   - `python platform/backend/manage.py migrate --settings=project.settings`
4. Ejecutar servidor:
   - `python platform/backend/manage.py runserver 0.0.0.0:8000 --settings=project.settings`

### Cargar datos sintéticos
1. Generar archivos:
   - `python platform/backend/scripts/generate_synthetic_data.py`
2. Cargar observaciones:
   - `python platform/backend/manage.py load_synthetic_observations --settings=project.settings`

### Tokens por usuario (opcional)
- Crear token: `python platform/backend/manage.py create_api_token --username demo_user`
- Usar token como `Authorization: Bearer <token>`; limita acceso a los recursos del usuario.

## Frontend

1. Variables de entorno:
   - `NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN=http://localhost:8000`
   - `NEXT_PUBLIC_PLATFORM_API_KEY=dev-secret-key` (o token de usuario)
2. Levantar Next.js en el directorio `frontend/`.
3. Rutas relevantes:
   - `/doctor/[token]` (pública)
   - `/observations/new` (protegida)
   - `/dashboards/*` (protegidas)
   - `/chat`

## Endpoints
- POST `/api/agents/v2/analyze` — protegido.
- GET `/api/agents/v2/status`
- POST `/api/lifecore/observations` — protegido.
- GET `/api/lifecore/observations/list` — protegido.
- GET `/api/lifecore/timeline` — protegido.
- POST `/api/doctor-link` — protegido.
- GET `/d/:token` — público.
