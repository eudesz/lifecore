# Plan Maestro: Escalado a 100 Tipos de Consultas Médicas (QuantIA)

Este documento detalla las 100 capacidades de consulta divididas en 10 dimensiones, y la arquitectura técnica para soportarlas.

## Arquitectura de Herramientas Necesaria

Para soportar este nivel de complejidad, pasaremos de herramientas de "búsqueda" a herramientas de "análisis".

1.  **`get_biometric_data` (Existente - Mejorar):** Soporte para agregaciones (promedios anuales, máximos históricos).
2.  **`get_clinical_events` (Existente):** Búsqueda fáctica de eventos.
3.  **`search_medical_documents` (Existente):** Búsqueda semántica cualitativa (RAG).
4.  **`compare_periods` (NUEVA):** Compara métricas entre dos rangos de fecha (ej. "Peso 2020 vs 2021").
5.  **`analyze_correlation` (NUEVA):** Detecta patrones entre dos variables (ej. "Pasos vs Peso").
6.  **`analyze_treatment_impact` (NUEVA):** Evalúa métricas antes y después de un evento (ej. "Colesterol después de iniciar Atorvastatina").
7.  **`calculate_health_score` (NUEVA):** Calculadoras médicas (IMC, Riesgo Cardiovascular simple).

---

## Las 100 Consultas (Categorizadas)

### Dimensión 1: Evolución Temporal y Tendencias (1-10)
*Enfoque: Cambios a largo plazo y patrones visuales.*
1.  "¿Cómo ha evolucionado mi peso en los últimos 10 años?"
2.  "Dame la tendencia de mi presión arterial desde 2015."
3.  "¿Cuál fue mi año con la glucosa más alta?"
4.  "Gráfica de mis pasos diarios del último mes."
5.  "¿He mantenido mi peso estable este año?"
6.  "Muestra la curva de crecimiento de mi IMC."
7.  "Tendencia de mis triglicéridos en la última década."
8.  "¿En qué meses suelo tener la presión más alta?" (Estacionalidad).
9.  "Evolución de mi frecuencia cardíaca en reposo."
10. "Resumen de signos vitales año por año."

### Dimensión 2: Análisis Comparativo (11-20)
*Enfoque: Contrastar periodos o estados.*
11. "Compara mi peso de 2020 con el de 2024."
12. "¿Cómo están mis niveles de colesterol respecto al año pasado?"
13. "Diferencia en mi actividad física: invierno vs verano."
14. "Promedio de glucosa este mes vs el mes anterior."
15. "¿Estoy durmiendo más ahora que hace 5 años?"
16. "Comparativa de mis análisis de sangre: antes vs después de la pandemia."
17. "¿Mi presión arterial es mejor por la mañana o por la noche?"
18. "Variación de peso entre mis 30 y 40 años."
19. "Comparar resultados de laboratorio de Enero vs Junio."
20. "¿He mejorado mi adherencia al tratamiento comparado con el año pasado?"

### Dimensión 3: Impacto de Tratamientos (21-35)
*Enfoque: Causa y efecto (Requiere `analyze_treatment_impact`).*
21. "¿Bajó mi colesterol después de empezar Atorvastatina?"
22. "¿Cómo afectó la Metformina a mi peso?"
23. "¿Hubo cambios en mi presión al iniciar Losartán?"
24. "Efecto de mi dieta (inicio Enero 2023) en mis triglicéridos."
25. "¿Mis niveles de glucosa se estabilizaron con la insulina?"
26. "¿Cuándo empecé a tomar Omeprazol y qué pasó con mi acidez?" (Requiere búsqueda en notas).
27. "¿He tenido efectos secundarios reportados por el antibiótico X?"
28. "Relación entre el inicio de mis caminatas y mi frecuencia cardíaca."
29. "Evaluar efectividad del tratamiento para la hipertensión."
30. "¿Qué dosis de Eutirox funcionó mejor para mi TSH?"
31. "Historial de cambios de dosis en mis medicamentos."
32. "¿Dejé de tomar algún medicamento por efectos adversos?"
33. "Métricas de salud antes y después de mi cirugía de 2018."
34. "Impacto de la suspensión del tratamiento X."
35. "¿Cuánto tardó en bajar mi fiebre tras el tratamiento?"

### Dimensión 4: Correlaciones y Estilo de Vida (36-45)
*Enfoque: Relaciones entre variables (Requiere `analyze_correlation`).*
36. "¿Hay relación entre mis pasos diarios y mi pérdida de peso?"
37. "¿Mi presión arterial sube cuando subo de peso?"
38. "¿Afecta mi calidad de sueño a mi glucosa al día siguiente?"
39. "¿Mi estado de ánimo se correlaciona con mi actividad física?"
40. "Relación entre consumo de sal (si registrado) y presión."
41. "¿Mis dolores de cabeza coinciden con picos de presión?"
42. "Correlación entre estrés y brotes de dermatitis."
43. "¿Hago menos ejercicio cuando tengo dolor articular?"
44. "Relación entre peso e ingesta calórica."
45. "¿Mis niveles de vitamina D afectan mi estado de ánimo?"

### Dimensión 5: Búsqueda Profunda en Documentos (RAG) (46-60)
*Enfoque: Datos no estructurados y cualitativos.*
46. "¿Qué dijo el cardiólogo sobre mi soplo en 2019?"
47. "Resúmeme los hallazgos de mi última resonancia magnética."
48. "Busca menciones de 'hígado graso' en mis ecografías."
49. "¿Algún doctor ha sugerido cirugía para mi rodilla?"
50. "¿Qué recomendaciones de dieta me dieron en la última consulta?"
51. "Busca antecedentes familiares de cáncer en mis historias clínicas."
52. "¿Se mencionó alguna alergia en mis reportes de urgencias?"
53. "Extrae las conclusiones de mi informe de alta hospitalaria."
54. "¿Qué razones dio el médico para cambiar mi medicación?"
55. "Lista todos los diagnósticos dermatológicos que he tenido."
56. "¿Hay observaciones sobre mi salud mental en las notas?"
57. "¿Qué vacunas me recomendaron en el viaje a Asia?"
58. "Busca resultados de biopsias en mi historial."
59. "¿Qué pronóstico me dieron para mi diabetes?"
60. "Recupera la interpretación del electrocardiograma de 2021."

### Dimensión 6: Eventos Clínicos y Línea de Tiempo (61-70)
*Enfoque: Hechos puntuales.*
61. "¿Cuándo fue mi última visita al oftalmólogo?"
62. "Lista todas mis cirugías ordenadas por fecha."
63. "¿Cuántas veces he ido a urgencias este año?"
64. "¿Cuándo me diagnosticaron hipotiroidismo?"
65. "Fecha de mi última vacuna de tétanos."
66. "Mostrar todos los eventos médicos de 2015."
67. "¿Quién fue el doctor que me atendió en mayo de 2022?"
68. "Historial de mis hospitalizaciones."
69. "¿Cuánto tiempo pasó entre mi primera consulta y el diagnóstico?"
70. "Lista de especialistas que he visitado."

### Dimensión 7: Salud Preventiva y Riesgos (71-80)
*Enfoque: Cálculos y proyecciones (Requiere `calculate_health_score`).*
71. "Calcula mi IMC actual y su clasificación."
72. "¿Estoy en riesgo cardiovascular según mis últimos datos?" (Framingham simplificado).
73. "¿Cuándo me toca mi próximo chequeo anual?"
74. "¿Tengo mis vacunas al día según mi edad?"
75. "Evalúa si cumplo la meta de 150 minutos de ejercicio semanal."
76. "¿Mi nivel de glucosa indica pre-diabetes?"
77. "Calcula mi presión arterial media (MAP)."
78. "Riesgo de osteoporosis según mis datos (edad/peso)."
79. "¿Mis niveles de HDL/LDL están en rango saludable?"
80. "Recomendaciones preventivas para mi edad y género."

### Dimensión 8: Gestión de Medicamentos (81-90)
*Enfoque: Inventario y logística.*
81. "¿Qué medicamentos estoy tomando actualmente?"
82. "¿Tengo alguna receta activa por vencer?"
83. "Lista de medicamentos crónicos vs temporales."
84. "¿Cuál es la dosis actual de mi pastilla para la presión?"
85. "Recordatorio de horario de mis medicamentos."
86. "¿Hay interacciones entre los medicamentos que tomo?" (Básico).
87. "¿He duplicado alguna medicación en el pasado?"
88. "Agrupa mis medicamentos por condición que tratan."
89. "¿Desde cuándo tomo Aspirina?"
90. "Historial de antibióticos tomados."

### Dimensión 9: Salud Específica / Condiciones (91-95)
*Enfoque: Visión centrada en la enfermedad.*
91. "Resumen completo de mi Diabetes (labs, meds, eventos)."
92. "Todo sobre mi Hipertensión."
93. "Historial de mis lesiones deportivas."
94. "Evolución de mi Asma."
95. "Seguimiento de mi embarazo (si aplica)."

### Dimensión 10: Administrativo y Resumen Ejecutivo (96-100)
*Enfoque: Meta-información.*
96. "Genera un resumen de salud para un nuevo doctor."
97. "¿Qué datos faltan en mi perfil?"
98. "Resumen ejecutivo de los últimos 5 años."
99. "Exportar mis datos principales."
100. "¿Quién tiene acceso a mis datos actualmente?"

