# Plan Maestro: Suite de 20 Herramientas para QuantIA (v3)
**Objetivo:** Crear el asistente de salud personal más avanzado del mundo.

Este plan expande la capacidad del agente de 8 a 20 herramientas especializadas, cubriendo todo el espectro de la salud del paciente: desde el análisis molecular (labs) hasta el estilo de vida y la predicción de riesgos.

---

## Dimensión 1: Bio-Analítica Profunda (El Cuerpo en Datos)
*Estas herramientas procesan datos duros para encontrar verdades ocultas.*

1.  **`analyze_lab_panels`** (NUEVA)
    *   **Función:** Interpreta paneles de laboratorio complejos (Hemograma, Perfil Lipídico). Detecta valores fuera de rango (H/L) y explica su significado clínico en contexto.
    *   *Uso:* "¿Qué significa mi colesterol LDL de 160 en mi último análisis?"

2.  **`analyze_wearable_metrics`** (NUEVA)
    *   **Función:** Análisis avanzado de métricas de relojes inteligentes: Variabilidad de frecuencia cardíaca (HRV), VO2 Max, Saturación de O2.
    *   *Uso:* "¿Está mejorando mi capacidad cardiovascular con el entrenamiento?"

3.  **`detect_symptom_patterns`** (NUEVA)
    *   **Función:** Busca en notas no estructuradas patrones de síntomas recurrentes (ej. "dolor de cabeza" cada lunes, o asociado a "estrés").
    *   *Uso:* "¿Desde cuándo sufro de migrañas y qué las detona?"

4.  **`compare_cohort_benchmarks`** (NUEVA)
    *   **Función:** Compara los datos del usuario con promedios poblacionales anónimos (Edad/Sexo).
    *   *Uso:* "¿Es normal mi presión arterial para un hombre de 45 años?"

5.  **`get_biometric_data`** (MEJORADA)
    *   **Mejora:** Soporte para multi-variable y agregaciones complejas (desviación estándar).

---

## Dimensión 2: Farmacología y Seguridad (Protección)
*Herramientas diseñadas para proteger al paciente y optimizar tratamientos.*

6.  **`check_drug_interactions`** (NUEVA)
    *   **Función:** Cruza la lista de medicamentos actuales con un nuevo fármaco o suplemento para alertar sobre interacciones peligrosas.
    *   *Uso:* "¿Puedo tomar Ibuprofeno si estoy usando Warfarina?"

7.  **`check_medication_adherence`** (NUEVA)
    *   **Función:** Calcula el porcentaje de cumplimiento de toma de medicamentos basado en registros o logs.
    *   *Uso:* "¿He sido constante con mi medicación este mes?"

8.  **`analyze_treatment_efficacy`** (Renombramiento de `analyze_treatment_impact`)
    *   **Mejora:** No solo mira métricas, sino que busca en notas del doctor palabras clave de "mejoría" o "efecto adverso".

9.  **`check_contraindications`** (NUEVA)
    *   **Función:** Verifica alergias conocidas y condiciones previas contra nuevos tratamientos sugeridos.
    *   *Uso:* "El doctor me recetó Penicilina, ¿es seguro para mí?"

10. **`get_vaccination_status`** (NUEVA)
    *   **Función:** Rastrea historial de vacunación y sugiere refuerzos pendientes según guías oficiales.
    *   *Uso:* "¿Estoy al día con mi vacuna del Tétanos?"

---

## Dimensión 3: Medicina Preventiva y Predictiva (El Futuro)
*Herramientas que miran hacia adelante para evitar problemas.*

11. **`calculate_risk_scores`** (NUEVA)
    *   **Función:** Calcula scores clínicos estándar (Framingham, ASCVD, FINDRISC) usando datos en tiempo real.
    *   *Uso:* "¿Cuál es mi riesgo cardiovascular a 10 años?"

12. **`get_preventive_screenings`** (NUEVA)
    *   **Función:** Genera una lista de chequeos pendientes (Colonoscopia, Mamografía, PSA) según edad, sexo y antecedentes.
    *   *Uso:* "¿Qué chequeos debería hacerme este año?"

13. **`get_family_genetic_risks`** (NUEVA)
    *   **Función:** Analiza el árbol genealógico (antecedentes familiares) para identificar riesgos hereditarios.
    *   *Uso:* "Dado que mi padre tuvo cáncer, ¿qué debo vigilar?"

14. **`predict_health_trajectory`** (EXPERIMENTAL)
    *   **Función:** Proyección lineal basada en tendencias actuales (ej. "Si sigues ganando peso a este ritmo, en 5 años tendrás obesidad tipo I").
    *   *Uso:* "¿Cómo estaré en 5 años si no cambio mis hábitos?"

---

## Dimensión 4: Estilo de Vida y Salud Mental (Holística)
*Salud más allá de la clínica.*

15. **`analyze_sleep_quality`** (NUEVA)
    *   **Función:** Correlaciona fases de sueño (REM, Profundo) con cansancio reportado o actividad diaria.
    *   *Uso:* "¿Por qué me siento tan cansado últimamente?"

16. **`analyze_nutritional_logs`** (NUEVA)
    *   **Función:** Analiza registros de dieta (si existen) o inferencias de notas para detectar deficiencias o excesos (Azúcar, Sodio).
    *   *Uso:* "¿Estoy consumiendo demasiado sodio?"

17. **`analyze_mental_wellbeing`** (NUEVA)
    *   **Función:** Análisis de sentimiento en notas de diario o check-ins de ánimo. Detecta tendencias depresivas o de ansiedad.
    *   *Uso:* "¿Ha mejorado mi estado de ánimo este mes?"

18. **`analyze_fitness_performance`** (NUEVA)
    *   **Función:** Analiza tipos de ejercicio, intensidad y frecuencia.
    *   *Uso:* "Resumen de mi actividad física anual."

---

## Dimensión 5: Gestión y Síntesis (Utilidad)

19. **`generate_doctor_summary`** (Especializada)
    *   **Función:** Genera un resumen técnico en lenguaje médico ("Paciente masculino de 45 años con antecedentes de...") listo para compartir.
    *   *Uso:* "Prepara un resumen para mi cardiólogo."

20. **`search_medical_knowledge_base`** (MEJORADA)
    *   **Mejora:** Además de buscar en documentos del paciente, permite buscar en una base de conocimientos médica confiable (Guías Clínicas) para dar contexto.
    *   *Uso:* "¿Qué dicen las guías sobre la presión arterial normal?"

---

## Plan de Implementación

1.  **Fase 1 (Core):** Implementar `analyze_lab_panels`, `calculate_risk_scores`, `check_drug_interactions`.
2.  **Fase 2 (Lifestyle):** Implementar `analyze_sleep_quality`, `analyze_wearable_metrics`.
3.  **Fase 3 (Prediction):** Implementar `predict_health_trajectory`, `get_preventive_screenings`.
4.  **Fase 4 (Data Filling):** Generar datos sintéticos avanzados para probar estas nuevas herramientas (logs de sueño, paneles de laboratorio detallados, genes).

