## Visión general de la app

La plataforma QuantIA ofrece dos experiencias claras, siempre centradas en **un solo paciente**:

- **Modo paciente** (app normal: `index` → `chat`): la persona ve su historia (timeline, grafo) y conversa con un asistente en lenguaje sencillo.
- **Modo médico** (acceso por link: `doctor/[token]`): un profesional accede de forma segura a los datos de ese paciente, ve paneles de métricas y habla con un asistente clínico.

En ambos modos, el comportamiento interno sigue el workflow del módulo de Stanford:

1. Formular una **pregunta clínica** sobre ese paciente.
2. Usar como fuente los datos de su EMR personal (timeline, labs, documentos, tratamientos, grafo).
3. Seleccionar y transformar datos relevantes (filtros de tiempo, categorías, condiciones).
4. Generar un análisis (texto + visualizaciones) adaptado al rol (paciente vs médico).

No se hacen análisis de cohortes ni investigación multi‑paciente: todo está enfocado en **un paciente a la vez**.

---

## Modo paciente (app por defecto)

### Landing y entrada

- **Landing (`/`)**:
  - Mensaje de valor: “Your Health Data, Decoded by AI”.
  - Botón **“Launch Platform”** que abre un selector de usuario (demo o usuario real).
  - Posiciona la app como un intérprete de la historia de salud de la propia persona.

### Vista principal paciente (`/chat`)

- **Estructura en tres bloques**:
  - **Cabecera**:
    - Branding de QuantIA, estado de sistema y botón **“Share Access”** para compartir datos con un médico.
  - **Columna izquierda – “Analysis View”**:
    - Subvista **Timeline**: línea de tiempo con eventos clínicos.
    - Subvista **Graph**: grafo de conocimiento personal.
  - **Columna derecha – “Neural Assistant”**:
    - Chat en lenguaje sencillo con el asistente de salud.
    - Selector de contexto: **General** vs **Context Aware** (usa filtros del timeline).

### Timeline del paciente

- Representa la historia clínica como una **línea temporal única**:
  - Eventos: diagnósticos, tratamientos, resultados de laboratorio, consultas, documentos, procedimientos, etc.
  - Filtros:
    - **Rango temporal** (años).
    - **Categorías** (diagnosis, treatment, lab, consultation, etc.).
    - **Condiciones** normalizadas (ej. diabetes, lupus), con colores y contadores.
  - Funciones:
    - Seleccionar un evento y ver:
      - Título y descripción.
      - Fecha exacta.
      - Métricas cercanas (peso, glucosa, presión) cuando apliquen.
      - Enlace al documento asociado (si existe).

Esto implementa el concepto de **patient timeline** del módulo: organizar datos del EMR en el tiempo para un solo paciente.

### Grafo de conocimiento personal

- Grafo centrado en el nodo **Paciente**, con conexiones a:
  - Condiciones.
  - Medicamentos.
  - Documentos.
  - Eventos.
- Funciones:
  - Visualización dinámica del grafo (zoom, centrado en nodos).
  - Colores por tipo de nodo (Patient, Condition, Medication, Document, Event).
  - Permite ver de forma intuitiva cómo se relacionan diagnósticos, tratamientos y pruebas.

### Chat paciente y workflow de pregunta → datos → análisis

- **Plantear la pregunta (Step 1)**:
  - El paciente formula preguntas en lenguaje natural:
    - “¿Qué ha pasado con mi azúcar en sangre en los últimos años?”
    - “¿Qué significa que tenga proteinuria?”
    - “¿Estoy mejor o peor que hace 5 años?”

- **Uso de datos del paciente (Step 2)**:
  - El asistente utiliza internamente:
    - Observaciones biométricas (peso, glucosa, presión, VO2, etc.).
    - Eventos de la línea de tiempo.
    - Documentos clínicos indexados (informes, notas, PDFs).
    - Tratamientos activos/pasados y su calendario.
    - Grafo de conocimiento alrededor de ese paciente.

- **Extracción y transformación (Step 3)**:
  - Dependiendo de la pregunta, el asistente:
    - Resumen la evolución de una condición concreta (p.ej. “historia de tu diabetes”).
    - Extrae los últimos labs relevantes y marca los que están fuera de rango.
    - Compara periodos (antes/después de un tratamiento, años distintos) para ese paciente.
    - Usa (cuando procede) relaciones del grafo para explicar cómo se conectan diagnósticos, medicamentos y eventos.

- **Análisis y explicación (Step 4)**:
  - Tipos de preguntas respondidas al paciente:
    - **Descriptivas**: resumen de datos, tendencias personales.
    - **Exploratorias**: “qué patrones se ven entre pasos y peso”, “cómo se relaciona el sueño con mi glucosa”.
    - **Predictivas ligeras / de riesgo**: estimaciones cualitativas (“parece un riesgo más alto/similar/bajo”) siempre con advertencias.
  - Estilo de respuesta:
    - Lenguaje sencillo, evitando jerga o explicándola (ej. “proteinuria: significa que hay proteína en la orina…”).
    - No da diagnósticos ni órdenes de tratamiento.
    - Propone preguntas para llevar al médico (“comenta con tu médico si…”).
    - Recuerda que la herramienta **no sustituye una consulta presencial**.

### Compartir con el médico (Share With Doctor)

- **Gestión de links por paciente**:
  - El usuario puede crear un link de solo lectura para un médico, que incluye:
    - **Caducidad**: 24 horas, 7 días o 30 días.
    - **Alcance opcional**:
      - Rango de fechas.
      - Condiciones específicas (ej. “solo relación con lupus”).
      - Categorías de datos (diagnosis, treatment, lab, consultation, event).
  - El usuario puede:
    - Ver todos los links activos (fecha de creación y vencimiento, estado activo/revocado).
    - Copiar un link al portapapeles.
    - Revocar un link.

Esta funcionalidad controla **qué porción de la historia de ese paciente** ve un médico concreto, sin exponer otros pacientes.

---

## Modo médico (acceso por link a un paciente)

### Acceso seguro vía token

- El médico accede a la app con una URL de la forma `/doctor/[token]`, generada por el paciente.
- El backend verifica:
  - Que el token exista y no esté revocado.
  - Que no haya caducado.
  - Que se respeten las restricciones de alcance (fechas, condiciones, categorías) definidas por el paciente.
- En la cabecera de la vista médica se muestra:
  - Branding QuantIA Professional.
  - Indicador de acceso seguro (“SECURE ACCESS · TOKEN VALID”).
  - ID interno del paciente.

### Panel clínico del paciente (Clinical Vitals)

- **Selección de métrica y rango temporal**:
  - El médico elige una métrica (ej. glucosa, peso, presión arterial, etc.).
  - Filtra por rango de fechas (desde/hasta).

- **Resumen cuantitativo**:
  - Valor más reciente (con unidad).
  - Media.
  - Mínimo y máximo.
  - Tendencia (sube, baja, estable) y variación porcentual aproximada.

- **Visualización de serie temporal**:
  - Gráfico de la métrica seleccionada en el rango indicado.
  - Permite visualizar picos, caídas y cambios en el tiempo.

- **Listado de registros recientes**:
  - Tabla con las últimas mediciones (fecha, valor, unidad).
  - Centrada en un número limitado de filas para revisión rápida.

- **Exportación**:
  - Botón para exportar los datos de esa métrica en ese paciente a CSV.

Todo esto se aplica exclusivamente al paciente vinculado al token: es una lectura detallada de su **patient‑feature matrix personal** (una sola fila con muchas columnas y fechas).

### Asistente clínico para ese paciente (AI Consultant)

- **Zona de conversación clínica**:
  - Pestaña “AI Consultant” con:
    - Historial de mensajes médico ↔ asistente.
    - Campo de entrada para preguntas clínicas.
  - Inicialmente, el asistente puede generar un **resumen clínico ejecutivo** del paciente:
    - Diagnósticos clave.
    - Tendencias importantes en labs/vitales.
    - Alertas recientes.

- **Preguntas típicas que el médico puede hacer**:
  - “Resume la situación clínica actual de este paciente”.
  - “¿Cómo han cambiado la glucosa y el peso en los últimos 3 años en este paciente?”.
  - “¿Qué tratamientos activos tiene y cómo ha respondido históricamente?”.
  - “¿Hay patrones llamativos entre el sueño, la actividad y los valores de glucosa de este paciente?”.

- **Estilo del modo médico**:
  - Usa lenguaje técnico cuando es útil (SLE, HbA1c, RR, etc.).
  - Se centra en:
    - Estratificación de riesgo para este paciente.
    - Patrones y tendencias en sus datos.
    - Contexto y limitaciones de los datos disponibles.
  - No pretende dictar guías clínicas oficiales:
    - Ofrece apoyo a la decisión, no sustitución del juicio del médico.
    - Marca explícitamente cuando algo es solo descriptivo o hay falta de evidencia.

- **Auditoría de la conversación**:
  - Los mensajes ligados a un token concreto pueden ser reconstruidos:
    - Con roles diferenciados (médico vs asistente clínico).
    - Solo para ese token/paciente.
  - Permite saber qué se preguntó y qué se respondió respecto a ese paciente.

---

## Comportamiento inteligente compartido (sin multi‑paciente)

### Tipos de preguntas (aplicado a un solo paciente)

Aunque internamente el modelo pueda distinguir tipos de pregunta, desde fuera se ve así:

- **Paciente**:
  - Recibe sobre todo respuestas **descriptivas** y de **explicación**:
    - “Qué significa X para ti”, “cómo han evolucionado tus datos”.
  - Alguna respuesta **predictiva ligera** (riesgo relativo simplificado) siempre con advertencias.

- **Médico**:
  - Puede hacer preguntas:
    - Descriptivas (resúmenes).
    - Exploratorias (patrones dentro de la historia del paciente).
    - Predictivas (estimaciones apoyadas en scores y tendencias individuales).
  - Siempre limitado a **un paciente**: no se construyen cohortes ni se comparan varios pacientes reales del sistema.

### Uso de datos del EMR personal

En ambos modos, el asistente se alimenta de:

- Línea de tiempo clínica personalizada.
- Observaciones biométricas y de estilo de vida.
- Tratamientos (activos e históricos).
- Documentos clínicos estructurados desde PDFs/notas.
- Grafo de conocimiento centrado en ese paciente.

No hay agregación entre pacientes ni construcción de cohortes internas.

### Diferencias de lenguaje y objetivo según rol

- **Modo paciente**:
  - Lenguaje sencillo y empático.
  - Explica conceptos médicos, evita jerga o la acompaña de definición breve.
  - Objetivo: comprensión, educación y apoyo para preparar la consulta con su médico.

- **Modo médico**:
  - Lenguaje técnico, estructura tipo informe.
  - Objetivo: acelerar la comprensión de la historia de ese paciente, resaltar riesgos y patrones, y servir de apoyo a la decisión clínica.


