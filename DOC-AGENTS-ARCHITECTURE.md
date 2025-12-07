# Documentación Técnica: Arquitectura de Chat y Agentes (v2)

Esta documentación describe la estructura interna del sistema de chat inteligente **QuantIA**, diseñado para actuar como un orquestador médico avanzado capaz de consultar, analizar y correlacionar datos de salud complejos.

## 1. Visión General del Flujo

El sistema no es un simple chatbot de preguntas y respuestas; es un **Agente Inteligente con Uso de Herramientas (Tool-Use Agent)**. Esto significa que el modelo de lenguaje (LLM) tiene "brazos" (funciones de código) para tocar la base de datos real del paciente antes de responder.

### Diagrama de Flujo Lógico

```mermaid
graph TD
    A[Usuario] -->|Pregunta| B(API: /api/agents/analyze)
    B --> C{Orquestador LLM (GPT-4o)}
    
    C -->|¿Necesita datos?| D[Decisión de Herramienta]
    C -->|Charla casual| E[Respuesta Directa]
    
    D -->|Fechas/Eventos| F[get_clinical_events]
    D -->|Biometría/Gráficos| G[get_biometric_data]
    D -->|Docs/Cualitativo| H[search_medical_documents (RAG)]
    D -->|Resúmenes| I[get_medical_summary_data]
    D -->|Análisis| J[compare/correlation/impact]
    
    F & G & H & I & J -->|Datos JSON| K[Contexto Enriquecido]
    K --> C
    C -->|Síntesis Final| L[Respuesta al Usuario]
```

## 2. Componentes Principales

### A. Controlador de API (`backend/apps/agents_v2/views.py`)
Es el punto de entrada.
- **Función `analyze`**: Recibe la consulta del usuario.
- **Gestión de Sesión**: Recupera o crea un `conversation_id`.
- **Memoria a Corto Plazo**: Carga los últimos 5 turnos de conversación para mantener el contexto.
- **Llamada a OpenAI**: Envía la consulta junto con las **Definiciones de Herramientas** disponibles.

### B. Definición de Herramientas (`backend/apps/agents_v2/tools.py`)
Aquí reside la lógica de negocio real. Cada función es una "habilidad" que el agente puede invocar.

| Herramienta | Descripción | Uso Típico |
|-------------|-------------|------------|
| `get_biometric_data` | Consulta SQL de `Observation`. Devuelve JSON estructurado. | "¿Cómo está mi glucosa?", "Dame mi peso de 2020". |
| `get_clinical_events` | Consulta `TimelineEvent`. Filtra por categorías. | "¿Cuándo fue mi última cirugía?", "¿Qué diagnósticos tengo?". |
| `search_medical_documents` | Búsqueda Semántica (Vectorial/RAG) en `Document`. | "¿Qué dijo el doctor sobre mi dieta?", "Síntomas de 2015". |
| `get_medical_summary_data` | "Super Tool" que agrega múltiples fuentes. | "Resumen de mis últimos 5 años", "Historia de mi diabetes". |
| `compare_health_periods` | Análisis estadístico comparativo entre dos rangos. | "Compara mi peso de 2020 vs 2023". |
| `analyze_correlation` | Busca relaciones entre dos variables métricas. | "¿Mis pasos influyen en mi peso?". |
| `analyze_treatment_impact` | Analiza métricas antes y después de un hito (fármaco). | "¿Funcionó la Metformina para mi glucosa?". |
| `calculate_health_score` | Cálculos derivados (ej. IMC). | "¿Cuál es mi IMC actual?". |

### C. System Prompt (El "Cerebro")
En `views.py`, definimos la personalidad y las reglas estrictas del agente.
- **Personalidad**: Asistente médico profesional, empático, basado en evidencia.
- **Reglas de Enrutamiento**: Instrucciones explícitas sobre qué herramienta usar (ej. *"Si preguntan fechas, usa SIEMPRE `get_clinical_events`"*). Esto reduce alucinaciones y errores de selección.

## 3. Estructura de Datos y Memoria

### Modelos Clave (`backend/apps/lifecore/models.py`)
- **`TimelineEvent`**: La columna vertebral temporal. Cada consulta, diagnóstico o medición crítica genera un evento aquí. Es lo que consume `get_clinical_events`.
- **`Document`**: Archivos no estructurados (PDFs, notas). Se indexan vectorialmente (FAISS) para búsqueda semántica.
- **`Observation`**: Datos duros (series de tiempo). Peso, presión, glucosa.

### Memoria de Conversación (`MemoryEpisode`)
- Cada interacción (pregunta usuario, respuesta agente, uso de tool) se guarda como un `MemoryEpisode`.
- **Persistencia**: Permite que el chat recuerde lo que se dijo hace 2 minutos o hace 2 meses (si implementamos recuperación de largo plazo).

## 4. Flujo de Ejecución: Un Ejemplo

**Usuario:** *"¿Cómo ha evolucionado mi diabetes desde que empecé la dieta?"*

1.  **API `analyze`**: Recibe la pregunta.
2.  **LLM (Paso 1)**: Analiza la intención. Detecta palabras clave: "evolución", "diabetes", "dieta" (posible tratamiento o evento).
3.  **Decisión**: El LLM decide llamar a `get_medical_summary_data(condition='diabetes', time_range='all')` y quizás `search_medical_documents(query='dieta impacto diabetes')`.
4.  **Ejecución**: El backend ejecuta esas funciones Python, consulta PostgreSQL y FAISS, y obtiene JSONs con datos.
5.  **LLM (Paso 2)**: Recibe los JSONs. Ve que la glucosa bajó de 140 a 110 y que hay notas sobre "mejoría por dieta".
6.  **Respuesta Final**: Genera texto natural: *"He analizado tu historial de diabetes. Desde 2015, tus niveles de glucosa han mostrado una tendencia descendente..."*

## 5. Extensibilidad

Para agregar una nueva capacidad (ej. "Recomendar dieta"):
1.  Crear función Python en `tools.py` (`recommend_diet`).
2.  Agregar definición JSON en `TOOL_DEFINITIONS` (`tools.py`).
3.  (Opcional) Actualizar `system_prompt` en `views.py` para guiar su uso.
4.  ¡Listo! El agente ahora "sabe" recomendar dietas basándose en tu lógica.

