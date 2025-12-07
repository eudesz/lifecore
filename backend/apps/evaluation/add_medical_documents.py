"""
Script para agregar documentos médicos variados para mejorar RAG
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.models import Document
from django.contrib.auth.models import User

# Usuario demo-alex
user = User.objects.get(username='demo-alex')

# Documentos médicos para diferentes categorías
documents = [
    {
        "title": "Informe de Sueño - Evaluación Mensual",
        "source": "sleep_study",
        "content": """
Evaluación del patrón de sueño del paciente durante el último mes.

Observaciones:
- Promedio de horas de sueño: 7.2 horas/noche
- Variabilidad significativa: rango de 6.0 a 8.3 horas
- Días con sueño insuficiente (<6h): 8 noches en el mes
- Calidad del sueño reportada: moderada

Recomendaciones:
- Establecer horario regular de sueño
- Evitar pantallas 1 hora antes de dormir
- Evaluar factores de estrés que puedan afectar el descanso

Próxima revisión: 1 mes
"""
    },
    {
        "title": "Evaluación de Actividad Física",
        "source": "activity_report",
        "content": """
Resumen de actividad física del paciente.

Métricas del último mes:
- Promedio diario de pasos: 7,010 pasos
- Días con >10,000 pasos: 12 días
- Días con <5,000 pasos: 5 días
- Nivel de actividad: MODERADO

El paciente muestra un nivel de actividad física aceptable pero con oportunidad de mejora.
Se recomienda aumentar gradualmente la actividad para alcanzar objetivo de 10,000 pasos diarios.

Nota: La actividad física regular contribuye positivamente al control glucémico y peso.
"""
    },
    {
        "title": "Seguimiento de Estado de Ánimo",
        "source": "mood_tracking",
        "content": """
Registro psicológico del paciente durante el último mes.

Estado de ánimo promedio: 6.8/10
- Días con estado de ánimo bajo (<5): 6 días
- Días con estado de ánimo positivo (>7): 18 días
- Tendencia general: ESTABLE con ligera mejoría

Factores identificados:
- Correlación positiva entre actividad física y estado de ánimo
- Días de menor actividad coinciden con estado de ánimo más bajo
- Calidad del sueño impacta significativamente el ánimo

Recomendaciones:
- Continuar con rutina de ejercicio
- Considerar técnicas de manejo de estrés
- Monitorear relación entre sueño y estado emocional
"""
    },
    {
        "title": "Control de Glucosa - Tendencias",
        "source": "glucose_monitoring",
        "content": """
Análisis de tendencias de glucosa en los últimos 6 meses.

Resultados:
- Promedio general: 115 mg/dL
- Tendencia: ASCENDENTE (incremento de 8 mg/dL vs 6 meses atrás)
- Glucosa en ayunas: 105-127 mg/dL
- Variabilidad: MODERADA

Episodios de hiperglucemia (>140 mg/dL): 23 registros
Valores dentro de rango objetivo: 68%

Observaciones:
- El incremento gradual sugiere necesidad de ajuste en tratamiento
- Adherencia a metformina: PARCIAL según reporte del paciente
- Se recomienda mejorar adherencia y considerar ajuste de dosis

Próxima HbA1c programada en 3 meses.
"""
    },
    {
        "title": "Monitoreo de Presión Arterial",
        "source": "bp_monitoring",
        "content": """
Seguimiento de presión arterial del último trimestre.

Resumen:
- Presión sistólica promedio: 128 mmHg
- Presión diastólica promedio: 82 mmHg
- Clasificación: PRE-HIPERTENSIÓN

Análisis temporal:
- Valores más altos en horario matutino
- Presión más controlada en tardes/noches
- 8 registros con sistólica >140 mmHg

El paciente muestra tendencia a pre-hipertensión que requiere monitoreo continuo.
Se recomienda:
- Reducir ingesta de sodio
- Mantener actividad física regular
- Control cada 2 semanas
- Considerar medicación si persiste elevación
"""
    },
    {
        "title": "Control de Peso y Composición Corporal",
        "source": "weight_management",
        "content": """
Evaluación de peso y tendencias en el último año.

Datos actuales:
- Peso actual: 85.6 kg
- Peso hace 6 meses: 80.4 kg
- Cambio: +5.2 kg (incremento de 6.5%)
- IMC actual: 28.9 (sobrepeso)

Tendencia: ASCENDENTE
- Incremento gradual pero consistente
- Promedio de ganancia: ~0.9 kg/mes

Factores contribuyentes:
- Adherencia parcial a plan alimenticio
- Nivel de actividad física moderado pero insuficiente
- Cambios en dieta reportados en última consulta

Recomendaciones:
- Retomar plan alimenticio estructurado
- Incrementar actividad física a 10,000 pasos/día
- Monitoreo mensual de peso
- Objetivo: estabilizar peso en 3 meses
"""
    },
    {
        "title": "Panel Lipídico - Resultados y Análisis",
        "source": "lipid_panel",
        "content": """
Resultados del panel lipídico completo (Fecha: 2025-10-15)

RESULTADOS:
- Colesterol Total: 198 mg/dL [<200 deseable]
- LDL (Colesterol malo): 118 mg/dL [<100 óptimo, <130 aceptable]
- HDL (Colesterol bueno): 46 mg/dL [>40 deseable, >60 óptimo]
- Triglicéridos: 170 mg/dL [<150 normal]
- Ratio Colesterol/HDL: 4.3 [<5.0 deseable]

INTERPRETACIÓN:
- Colesterol total: LIMÍTROFE
- LDL: ACEPTABLE pero puede mejorar
- HDL: BAJO (factor de riesgo cardiovascular)
- Triglicéridos: ELEVADOS

RECOMENDACIONES:
1. Aumentar HDL mediante:
   - Ejercicio aeróbico regular
   - Alimentos ricos en omega-3
   - Reducir carbohidratos simples

2. Reducir triglicéridos:
   - Limitar azúcares y alcohol
   - Control de peso
   - Aumentar fibra dietética

3. Seguimiento en 6 meses con nuevo panel lipídico

Riesgo cardiovascular: MODERADO
"""
    },
    {
        "title": "Nota de Consulta - Ajuste de Tratamiento",
        "source": "consultation_note",
        "content": """
Consulta de seguimiento (Fecha: 2025-11-01)

MOTIVO: Control de diabetes tipo 2 y evaluación de parámetros metabólicos

HALLAZGOS:
- Glucosa en ayunas: 127 mg/dL (elevada)
- Peso: 85.6 kg (incremento desde última visita)
- Presión arterial: 132/84 mmHg (pre-hipertensión)
- Estado general: BUENO

REPORTE DEL PACIENTE:
- Adherencia a metformina: "a veces olvido tomas"
- Dieta: "he comido más carbohidratos últimamente"
- Ejercicio: "camino 30-40 min, 4-5 días/semana"
- Sueño: "variable, entre 6-8 horas"
- Estado de ánimo: "mayormente bien, algunos días difíciles"

PLAN:
1. Reforzar adherencia a metformina (establecer alarmas)
2. Consulta con nutricionista para plan alimenticio
3. Objetivo de pérdida de peso: 4-5 kg en 3 meses
4. Monitoreo semanal de glucosa
5. Control en 1 mes con laboratorios

SEGUIMIENTO: Próxima cita 2025-12-01
"""
    }
]

print("Agregando documentos médicos...")
for doc_data in documents:
    doc, created = Document.objects.get_or_create(
        user=user,
        title=doc_data["title"],
        defaults={
            "source": doc_data["source"],
            "content": doc_data["content"]
        }
    )
    if created:
        print(f"✓ Creado: {doc.title}")
    else:
        print(f"  Ya existe: {doc.title}")

print(f"\n✅ Total documentos para {user.username}: {Document.objects.filter(user=user).count()}")

