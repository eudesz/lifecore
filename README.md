# Platform Monorepo (LifeCore)

Estructura preparada para producción con separación clara de backend, frontend, datos sintéticos y operaciones.

- backend/: Django + apps `agents_v2`, `memory`, `consent`, `timeline`, `api`.
- frontend/: Next.js + dashboards.
- docs/: documentación técnica y contratos.
- ops/: despliegue (compose/helm), configuración y runbooks.
- sample_data/: datos sintéticos y fixtures.

Feature flags:
- FEATURE_LIFECORE
- FEATURE_AGENTS_V2

Ver `../docs/implementation_checklist.md` para el plan detallado.
