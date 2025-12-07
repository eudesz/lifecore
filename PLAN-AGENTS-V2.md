# Plan de Capacidades Cognitivas y Arquitectura de Agentes (The 30-Query Plan)

Este documento define las capacidades que el Agente de IA de QuantIA debe tener para responder consultas complejas sobre el historial médico sintético de 50 años.

## Parte 1: Las 30 Consultas Complejas (Test Suite)

Estas preguntas guiarán el desarrollo de las herramientas (Tools) del agente.

### A. Análisis Temporal y Tendencias (Requiere SQL + Rango de Fechas)
1.  "¿Cómo ha variado mi **peso** promedio anual desde que nací hasta hoy?"
2.  "Muéstrame una gráfica de mi **presión arterial** (sistólica y diastólica) durante los últimos 5 años."
3.  "¿Cuál fue mi nivel de **glucosa** más alto registrado en la década del 2010?"
4.  "Compara mi cantidad de **pasos diarios** de cuando tenía 20 años vs ahora."
5.  "¿En qué año tuve la mayor volatilidad en mi peso?"

### B. Correlación de Eventos y Métricas (Requiere Timeline + SQL)
6.  "¿Empezó a bajar mi **peso** después de que me recetaron **Metformina**?"
7.  "¿Cómo estaba mi **presión arterial** el mes antes de mi diagnóstico de **Diabetes Tipo 2**?"
8.  "¿Hubo algún cambio en mis **pasos diarios** (wearables) después de mi cirugía en 2018?"
9.  "¿Mis niveles de **glucosa** estaban controlados antes de iniciar el tratamiento farmacológico?"
10. "¿Coincidió mi aumento de peso con el periodo donde dejé de hacer ejercicio (bajos pasos)?"

### C. Búsqueda Semántica Profunda (Requiere Vector Store)
11. "¿Qué preocupaciones ha mencionado el doctor recurrentemente en sus **notas clínicas** sobre mi dieta?"
12. "Busca en los **reportes de laboratorio** cualquier mención de 'anemia' o 'hierro bajo'."
13. "Resúmeme la evolución de mi estado de ánimo según las **transcripciones** de las consultas."
14. "¿Hay alguna nota médica que mencione efectos secundarios de la medicación?"
15. "¿Qué recomendaciones de estilo de vida me dieron en los reportes de 2015?"

### D. Gestión Farmacológica y Tratamientos (Requiere Timeline/Treatments)
16. "¿Qué medicamentos estoy tomando **actualmente** y cuál es la dosis?"
17. "¿Cuándo fue la última vez que se ajustó mi dosis de **Metformina**?"
18. "Hazme una lista cronológica de todos los tratamientos que he recibido desde los 30 años."
19. "¿He tomado antibióticos en los últimos 2 años?"
20. "¿Cuál ha sido el tratamiento más largo que he seguido?"

### E. Consultas de "Razonamiento Médico Complejo" (Híbrido Total)
21. "**Analiza mi salud integral en 2019**: combina mis laboratorios, notas del doctor y mis signos vitales de ese año."
22. "¿Existe alguna discrepancia entre lo que dicen los reportes de laboratorio (PDFs) y lo que anotó el doctor ese día?"
23. "Basado en mi historial de los últimos 50 años, ¿cuáles son mis 3 mayores factores de riesgo actuales?"
24. "Redacta un resumen de mi historia clínica para un nuevo cardiólogo, enfocándote en mi hipertensión."
25. "¿Mis síntomas descritos en las notas coinciden con los picos de presión arterial registrados?"

### F. Preguntas de "Curiosidad del Paciente"
26. "¿Cuánto pesaba cuando nací?"
27. "¿Cuántos kilómetros he caminado en total en los últimos 10 años (sumando pasos)?"
28. "¿Cuál es la palabra que más repiten los doctores en mis reportes?"
29. "¿Tengo algún vacío de información médica (años sin datos)?"
30. "Si sigo la tendencia de los últimos 3 años, ¿cuánto pesaría en 2030?" (Proyección simple).

---

## Parte 2: Arquitectura de Agentes Multi-Herramienta

El agente dejará de ser una simple cadena RAG (Retrieval-Augmented Generation) para convertirse en un **Agente ReAct / Function Calling**.

### Herramientas (Tools) Propuestas

El LLM tendrá acceso a estas funciones Python:

#### 1. `get_biometric_data(metric, start_date=None, end_date=None)`
- **Descripción:** Obtiene series temporales de datos biométricos estructurados.
- **Fuente:** Base de datos SQL (Tabla `Observation`).
- **Parámetros:**
  - `metric`: string (e.g., 'weight', 'glucose', 'systolic_bp', 'steps').
  - `start_date`: string (ISO date).
  - `end_date`: string (ISO date).
- **Output:** JSON con lista de valores y fechas.
- **Caso de uso:** Gráficas, promedios, máximos/mínimos, tendencias numéricas.

#### 2. `search_medical_documents(query, year_filter=None, doc_type=None)`
- **Descripción:** Realiza una búsqueda semántica en los documentos indexados.
- **Fuente:** Vector Store (FAISS).
- **Parámetros:**
  - `query`: string (La pregunta o concepto a buscar).
  - `year_filter`: int (Opcional, para limitar a un año específico).
- **Output:** Lista de fragmentos de texto relevantes con metadatos.
- **Caso de uso:** Entender notas médicas, interpretar reportes PDF, buscar síntomas cualitativos.

#### 3. `get_clinical_events(category=None)`
- **Descripción:** Recupera eventos hitos de la historia clínica (diagnósticos, cirugías, tratamientos).
- **Fuente:** Base de datos SQL (Tabla `TimelineEvent` y `Treatment`).
- **Parámetros:**
  - `category`: string (e.g., 'diagnosis', 'treatment', 'surgery').
- **Output:** JSON con eventos, fechas y detalles.
- **Caso de uso:** Saber cuándo empezó una enfermedad, qué medicamentos toma, historial quirúrgico.

### Flujo de Ejecución

1.  **Entrada:** Usuario envía pregunta.
2.  **Razonamiento (LLM):** El modelo analiza la intención.
    *   *¿Necesito datos numéricos?* -> Llama a `get_biometric_data`.
    *   *¿Necesito leer reportes?* -> Llama a `search_medical_documents`.
    *   *¿Necesito fechas de eventos?* -> Llama a `get_clinical_events`.
    *   *¿Necesito todo?* -> Llama a múltiples herramientas secuencialmente.
3.  **Ejecución:** El backend ejecuta las funciones solicitadas.
4.  **Síntesis:** El LLM recibe los datos crudos (JSON/Texto) y genera la respuesta final en lenguaje natural, citando las fuentes.

