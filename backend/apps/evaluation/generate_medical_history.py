"""
Generador de Historial Médico Completo - 5 Años
Genera ~1,100 documentos médicos realistas correlacionados con datos existentes
"""
import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.models import Document, Observation
from django.contrib.auth.models import User

# Usuario objetivo
USER = None

def get_user():
    global USER
    if USER is None:
        USER = User.objects.get(username='demo-alex')
    return USER

def get_date(days_ago: int) -> datetime:
    """Fecha hace X días"""
    return datetime.now() - timedelta(days=days_ago)

def get_observation_avg(metric: str, start_date: datetime, end_date: datetime) -> float:
    """Obtener promedio de observaciones en un periodo"""
    obs = Observation.objects.filter(
        user=get_user(),
        code=metric,
        taken_at__gte=start_date,
        taken_at__lte=end_date
    )
    values = [float(o.value) for o in obs]
    return sum(values) / len(values) if values else 0

# ============================================================================
# CATEGORÍA 1: LABORATORIOS
# ============================================================================

def generate_panel_lipidico(date: datetime, num: int) -> Dict[str, Any]:
    """Panel lipídico - cada 6 meses"""
    # Obtener datos reales de colesterol si existen
    ldl = random.uniform(100, 140)
    hdl = random.uniform(40, 55)
    trig = random.uniform(140, 200)
    total = ldl + hdl + (trig / 5)
    
    ratio = total / hdl
    riesgo = "BAJO" if ratio < 3.5 else "MODERADO" if ratio < 5 else "ALTO"
    
    return {
        "title": f"Panel Lipídico - {date.strftime('%Y-%m-%d')}",
        "source": f"lab_lipids_{num}",
        "content": f"""PANEL LIPÍDICO COMPLETO
Fecha: {date.strftime('%d de %B de %Y')}
Paciente: Alexander (demo-alex)
Médico solicitante: Dr. García - Medicina Interna

RESULTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analito                  Resultado    Referencia      Estado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Colesterol Total         {total:.1f} mg/dL   <200           {'✓ Normal' if total < 200 else '⚠ Elevado'}
LDL (malo)              {ldl:.1f} mg/dL   <100 óptimo    {'✓ Óptimo' if ldl < 100 else '⚠ Elevado'}
HDL (bueno)             {hdl:.1f} mg/dL   >40 deseable   {'✓ Normal' if hdl > 40 else '⚠ Bajo'}
Triglicéridos           {trig:.1f} mg/dL   <150           {'✓ Normal' if trig < 150 else '⚠ Elevado'}
VLDL                    {trig/5:.1f} mg/dL   <30            {'✓ Normal' if trig/5 < 30 else '⚠ Elevado'}
Ratio Colesterol/HDL    {ratio:.2f}        <5.0           {'✓ Deseable' if ratio < 5 else '⚠ Riesgo'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERPRETACIÓN:
Riesgo cardiovascular estimado: {riesgo}

{'El perfil lipídico muestra valores dentro de rangos aceptables.' if ratio < 4 else 'Se recomienda intervención para reducir LDL y aumentar HDL.'}

RECOMENDACIONES:
1. {'Mantener dieta saludable' if ldl < 130 else 'Reducir grasas saturadas en la dieta'}
2. {'Continuar ejercicio regular' if hdl > 45 else 'Incrementar actividad aeróbica (30-45 min, 5 días/semana)'}
3. {'Monitoreo en 12 meses' if ratio < 4 else 'Control en 6 meses con nuevo panel'}
4. {'Considerar estatina' if ldl > 130 else 'Mantener tratamiento actual'}

Fecha de próximo control: {(date + timedelta(days=180)).strftime('%Y-%m-%d')}
"""
    }

def generate_hba1c(date: datetime, num: int) -> Dict[str, Any]:
    """HbA1c - cada 3 meses"""
    # Correlacionar con glucosas del periodo
    start = date - timedelta(days=90)
    avg_glucose = get_observation_avg('glucose', start, date)
    
    # Fórmula aproximada: HbA1c ≈ (avg_glucose + 46.7) / 28.7
    hba1c = (avg_glucose + 46.7) / 28.7 if avg_glucose > 0 else random.uniform(6.0, 7.5)
    
    control = "EXCELENTE" if hba1c < 6.5 else "BUENO" if hba1c < 7.0 else "ACEPTABLE" if hba1c < 8.0 else "REQUIERE MEJORA"
    
    return {
        "title": f"HbA1c (Hemoglobina Glicada) - {date.strftime('%Y-%m-%d')}",
        "source": f"lab_hba1c_{num}",
        "content": f"""HEMOGLOBINA GLICADA (HbA1c)
Fecha: {date.strftime('%d de %B de %Y')}
Paciente: Alexander (demo-alex)
Diagnóstico: Diabetes Mellitus Tipo 2

RESULTADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HbA1c: {hba1c:.2f}%

Valor de referencia:
  < 5.7%    : Sin diabetes
  5.7-6.4%  : Prediabetes  
  ≥ 6.5%    : Diabetes
  
Meta para diabéticos: < 7.0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERPRETACIÓN:
Control glucémico: {control}

Este valor refleja el promedio de glucosa en los últimos 2-3 meses.
Glucosa promedio estimada: {avg_glucose:.1f} mg/dL

{'✓ El control es adecuado, continuar con el plan actual.' if hba1c < 7.0 else '⚠ Se requiere intensificar el tratamiento para alcanzar meta <7.0%'}

TENDENCIA:
{'📉 Mejoría respecto a valores previos' if random.random() > 0.5 else '📈 Leve incremento, revisar adherencia'}

RECOMENDACIONES:
1. {'Mantener adherencia a metformina' if hba1c < 7.0 else 'Considerar ajuste de dosis de metformina'}
2. Continuar monitoreo de glucosa capilar
3. {'Reforzar plan alimenticio' if hba1c >= 7.0 else 'Mantener plan alimenticio'}
4. Próximo HbA1c en 3 meses

Médico: Dr. García - Endocrinología
"""
    }

def generate_panel_metabolico(date: datetime, num: int) -> Dict[str, Any]:
    """Panel metabólico completo"""
    return {
        "title": f"Panel Metabólico Completo - {date.strftime('%Y-%m-%d')}",
        "source": f"lab_metabolic_{num}",
        "content": f"""PANEL METABÓLICO COMPLETO (CMP)
Fecha: {date.strftime('%d de %B de %Y')}
Paciente: Alexander (demo-alex)

RESULTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test                    Resultado    Referencia      Estado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNCIÓN RENAL:
Creatinina             {random.uniform(0.8, 1.2):.2f} mg/dL   0.7-1.3        ✓ Normal
BUN                    {random.randint(10, 20)} mg/dL      7-20           ✓ Normal
TFG estimada           {random.randint(85, 110)} mL/min    >90            ✓ Normal

ELECTROLITOS:
Sodio (Na)             {random.randint(136, 145)} mEq/L     136-145        ✓ Normal
Potasio (K)            {random.uniform(3.5, 5.0):.1f} mEq/L     3.5-5.0        ✓ Normal
Cloruro (Cl)           {random.randint(98, 107)} mEq/L      98-107         ✓ Normal
CO2                    {random.randint(23, 29)} mEq/L      23-29          ✓ Normal

FUNCIÓN HEPÁTICA:
ALT (GPT)              {random.randint(15, 40)} U/L        <40            ✓ Normal
AST (GOT)              {random.randint(15, 37)} U/L        <37            ✓ Normal
Bilirrubina total      {random.uniform(0.3, 1.0):.1f} mg/dL    0.3-1.2        ✓ Normal
Fosfatasa alcalina     {random.randint(40, 130)} U/L        40-130         ✓ Normal

PROTEÍNAS:
Proteínas totales      {random.uniform(6.5, 8.0):.1f} g/dL     6.0-8.0        ✓ Normal
Albúmina               {random.uniform(3.5, 5.0):.1f} g/dL     3.5-5.0        ✓ Normal

GLUCOSA:
Glucosa en ayunas      {random.randint(95, 135)} mg/dL     70-100         {'✓ Controlada' if random.random() > 0.3 else '⚠ Elevada'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERPRETACIÓN GENERAL:
✓ Función renal: Normal, sin signos de nefropatía diabética
✓ Función hepática: Normal, metformina bien tolerada
✓ Electrolitos: Balanceados

SEGUIMIENTO:
- Continuar monitoreo trimestral
- Mantener hidratación adecuada
- Control de función renal (importante en diabetes)
"""
    }

# ============================================================================
# CATEGORÍA 2: CONSULTAS MÉDICAS
# ============================================================================

def generate_consulta_control(date: datetime, num: int) -> Dict[str, Any]:
    """Consulta de control trimestral"""
    # Obtener datos reales del periodo
    start = date - timedelta(days=90)
    avg_glucose = get_observation_avg('glucose', start, date)
    avg_weight = get_observation_avg('weight', start, date)
    avg_bp_sys = get_observation_avg('blood_pressure_systolic', start, date)
    
    return {
        "title": f"Consulta de Control - {date.strftime('%Y-%m-%d')}",
        "source": f"consultation_{num}",
        "content": f"""NOTA DE CONSULTA MÉDICA - CONTROL TRIMESTRAL
Fecha: {date.strftime('%d de %B de %Y, %H:%M')}
Paciente: Alexander, 45 años
Diagnóstico principal: Diabetes Mellitus Tipo 2
Médico: Dr. Roberto García - Medicina Interna

MOTIVO DE CONSULTA:
Control programado de diabetes mellitus tipo 2

SUBJETIVO (Reporte del paciente):
- Adherencia a metformina: {"Buena (>80%)" if random.random() > 0.3 else "Regular (60-80%)"}
- Automonitoreo de glucosa: {"Consistente" if random.random() > 0.5 else "Intermitente"}
- Dieta: {"Siguiendo plan" if random.random() > 0.4 else "Ha habido algunas transgresiones"}
- Ejercicio: {"Camina 30-40 min, 4-5 días/semana" if random.random() > 0.5 else "Irregular, 2-3 días/semana"}
- Síntomas: {"Niega poliuria, polidipsia, visión borrosa" if random.random() > 0.7 else "Reporta ocasional polidipsia"}

OBJETIVO:
Signos vitales:
- Presión arterial: {avg_bp_sys:.0f}/{random.randint(75, 85)} mmHg
- Frecuencia cardíaca: {random.randint(68, 82)} lpm
- Peso: {avg_weight:.1f} kg (IMC: {avg_weight / (1.75 ** 2):.1f})
- Temperatura: 36.{random.randint(5, 8)}°C

Examen físico:
- Estado general: Bueno, alerta, orientado
- Cardiovascular: Ruidos cardíacos rítmicos, no soplos
- Pulmonar: Murmullo vesicular conservado
- Abdomen: Blando, no doloroso, no masas
- Extremidades: Pulsos periféricos presentes, no edema
- Pies: Sin lesiones, sensibilidad conservada

EVALUACIÓN:
Control glucémico actual: {"ADECUADO" if avg_glucose < 120 else "REGULAR" if avg_glucose < 140 else "REQUIERE MEJORA"}
- Glucosa promedio últimos 3 meses: {avg_glucose:.1f} mg/dL
- {'✓ Dentro de metas' if avg_glucose < 130 else '⚠ Por encima de meta'}

Presión arterial: {"Controlada" if avg_bp_sys < 130 else "Limítrofe, requiere monitoreo"}

Peso: {"Estable" if random.random() > 0.5 else "Leve incremento de 1.5 kg desde última visita"}

PLAN:
1. MEDICACIÓN:
   - Metformina 850 mg: continuar 1 tableta cada 12 horas
   {'   - Considerar ajuste de dosis en próxima visita' if avg_glucose > 130 else ''}

2. LABORATORIOS:
   - HbA1c: solicitar para próxima visita
   - Panel lipídico: pendiente en 3 meses
   - Función renal: solicitar creatinina y microalbuminuria

3. ESTILO DE VIDA:
   - Reforzar adherencia a plan alimenticio
   - Meta de pasos: 8,000-10,000 diarios
   - Continuar registro de glucosas

4. SEGUIMIENTO:
   - Próxima consulta en 3 meses
   - Contactar si glucosas >180 mg/dL persistentes
   - Renovación de receta de metformina x 3 meses

EDUCACIÓN PROPORCIONADA:
- Importancia del control glucémico para prevenir complicaciones
- Técnica correcta de medición de glucosa
- Signos de alarma (hipoglucemia, hiperglucemia)

Firma: Dr. Roberto García
Cédula profesional: 123456
"""
    }

def generate_consulta_nutricion(date: datetime, num: int) -> Dict[str, Any]:
    """Consulta con nutrición"""
    weight = get_observation_avg('weight', date - timedelta(days=7), date)
    
    return {
        "title": f"Consulta de Nutrición - {date.strftime('%Y-%m-%d')}",
        "source": f"nutrition_{num}",
        "content": f"""CONSULTA DE NUTRICIÓN CLÍNICA
Fecha: {date.strftime('%d de %B de %Y')}
Paciente: Alexander (demo-alex)
Nutrióloga: Lic. María Fernández

ANTROPOMETRÍA:
- Peso actual: {weight:.1f} kg
- Talla: 1.75 m
- IMC: {weight / (1.75 ** 2):.1f} kg/m² ({'Sobrepeso' if weight / (1.75 ** 2) > 25 else 'Normal'})
- Circunferencia abdominal: {random.randint(90, 105)} cm ({'⚠ Riesgo cardiovascular' if random.randint(90, 105) > 94 else '✓ Adecuado'})

EVALUACIÓN DIETÉTICA:
Recordatorio de 24 horas:
- Desayuno: {'Adecuado en porciones' if random.random() > 0.4 else 'Exceso de carbohidratos'}
- Comida: {'Balanceada' if random.random() > 0.5 else 'Baja en vegetales'}
- Cena: {'Ligera, apropiada' if random.random() > 0.5 else 'Tardía y alta en calorías'}
- Colaciones: {'2 al día, adecuadas' if random.random() > 0.6 else 'Inconsistentes'}

Distribución de macronutrientes actual:
- Carbohidratos: {'45-50%' if random.random() > 0.5 else '60% (excesivo)'}
- Proteínas: 20-25%
- Grasas: {'25-30%' if random.random() > 0.5 else '35% (elevado)'}

DIAGNÓSTICO NUTRICIONAL:
- Diabetes Mellitus Tipo 2 con {'buen' if random.random() > 0.5 else 'regular'} control
- {'IMC en rango de sobrepeso' if weight / (1.75 ** 2) > 25 else 'Peso saludable'}
- {'Consumo elevado de carbohidratos simples' if random.random() > 0.4 else 'Dieta balanceada en general'}

PLAN ALIMENTICIO PERSONALIZADO:

1. OBJETIVOS:
   - Mantener glucosa en ayunas 80-130 mg/dL
   - Glucosa postprandial <180 mg/dL
   - {'Reducir 0.5-1 kg/mes' if weight / (1.75 ** 2) > 25 else 'Mantener peso actual'}
   - Mejorar perfil lipídico

2. PRESCRIPCIÓN CALÓRICA:
   - VCT: {random.randint(1600, 1900)} kcal/día
   - 45-50% carbohidratos (preferir complejos)
   - 20-25% proteínas (magras)
   - 25-30% grasas (preferir insaturadas)

3. DISTRIBUCIÓN DE COMIDAS:
   - 5 tiempos: 3 comidas principales + 2 colaciones
   - Horarios regulares (importante para control glucémico)
   - Colación nocturna si toma metformina en la cena

4. RECOMENDACIONES ESPECÍFICAS:

CARBOHIDRATOS (45-50% VCT):
   ✓ Preferir: granos enteros, leguminosas, vegetales
   ✓ Limitar: harinas refinadas, azúcares simples
   ✓ Método del plato: 1/4 del plato
   ✓ Conteo de carbohidratos: 45-60g por comida

PROTEÍNAS (20-25% VCT):
   ✓ Pollo, pescado, pavo sin piel
   ✓ Leguminosas (también aportan fibra)
   ✓ Huevo (entero, 4-7 por semana)
   ✗ Limitar carnes rojas grasas

GRASAS (25-30% VCT):
   ✓ Aceite de oliva, aguacate, nueces
   ✓ Pescados grasos (omega-3)
   ✗ Evitar grasas trans y saturadas

FIBRA:
   - Meta: 25-30 g/día
   - Ayuda a control glucémico y saciedad
   - Vegetales en cada comida

HIDRATACIÓN:
   - 2-2.5 litros de agua al día
   - Evitar bebidas azucaradas y jugos

5. EJEMPLO DE MENÚ DIARIO:

DESAYUNO (7:00 AM):
- 2 claras de huevo + 1 huevo entero
- 2 tortillas de maíz pequeñas
- 1 taza de frijoles
- 1 taza de papaya
- Café o té sin azúcar

COLACIÓN MATUTINA (10:00 AM):
- 1 manzana mediana
- 10 almendras

COMIDA (14:00 PM):
- Pechuga de pollo a la plancha (120g)
- 1 taza de arroz integral
- Ensalada abundante
- 1 cucharada de aceite de oliva
- Agua de jamaica sin azúcar

COLACIÓN VESPERTINA (17:00 PM):
- 1 taza de yogurt griego natural
- 1/2 taza de fresas

CENA (20:00 PM):
- Filete de pescado al horno (150g)
- 2 tortillas de maíz
- Verduras al vapor
- Ensalada
- 1 mandarina

6. SEGUIMIENTO:
   - Próxima cita en 4 semanas
   - Llevar registro de alimentos (3 días)
   - Monitorear glucosas pre y postprandiales
   - Pesarse semanalmente

EDUCACIÓN NUTRICIONAL PROPORCIONADA:
✓ Método del plato
✓ Lectura de etiquetas nutricionales
✓ Porciones adecuadas
✓ Opciones para comer fuera de casa

Lic. María Fernández
Nutrióloga Clínica - Cédula 234567
"""
    }

# ============================================================================
# CATEGORÍA 3: PRESCRIPCIONES
# ============================================================================

def generate_prescripcion_metformina(date: datetime, num: int) -> Dict[str, Any]:
    """Receta de metformina"""
    return {
        "title": f"Prescripción: Metformina - {date.strftime('%Y-%m-%d')}",
        "source": f"prescription_metformin_{num}",
        "content": f"""RECETA MÉDICA
Fecha: {date.strftime('%d de %B de %Y')}

DATOS DEL PACIENTE:
Nombre: Alexander
Edad: 45 años
Diagnóstico: Diabetes Mellitus Tipo 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rp/

1. METFORMINA 850 mg
   Presentación: Tabletas
   Cantidad: 180 tabletas
   
   INDICACIONES:
   Tomar 1 tableta cada 12 horas
   (1 en el desayuno y 1 en la cena)
   Con alimentos para reducir molestias gastrointestinales
   
   Duración del tratamiento: 3 meses
   
   PRECAUCIONES:
   - No suspender sin indicación médica
   - Si olvida una dosis, tomarla en cuanto lo recuerde
   - No duplicar dosis
   - Suspender 48h antes de estudios con contraste
   - Contactar si presenta náuseas, vómito o dolor abdominal severo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MECANISMO DE ACCIÓN:
La metformina reduce la producción de glucosa en el hígado y
mejora la sensibilidad a la insulina en tejidos periféricos.

EFECTOS SECUNDARIOS COMUNES (generalmente leves):
- Náuseas, diarrea (primeras semanas)
- Malestar abdominal
- Sabor metálico

ADVERTENCIAS IMPORTANTES:
⚠ Suspender si presenta deshidratación severa
⚠ Informar si requiere cirugía o procedimientos
⚠ Evitar consumo excesivo de alcohol

SEGUIMIENTO:
- Control de glucosa capilar según indicaciones
- Laboratorios de control en 3 meses
- Próxima consulta: {(date + timedelta(days=90)).strftime('%Y-%m-%d')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dr. Roberto García
Medicina Interna
Cédula profesional: 123456
Tel: (555) 123-4567

Fecha de expedición: {date.strftime('%Y-%m-%d')}
Vigencia de receta: 6 meses
"""
    }

# ============================================================================
# CATEGORÍA 4: REPORTES DE SEGUIMIENTO
# ============================================================================

def generate_reporte_mensual_glucosa(date: datetime, num: int) -> Dict[str, Any]:
    """Reporte mensual de glucosa"""
    start = date - timedelta(days=30)
    
    # Obtener datos reales
    obs = Observation.objects.filter(
        user=get_user(),
        code='glucose',
        taken_at__gte=start,
        taken_at__lte=date
    ).order_by('taken_at')
    
    values = [float(o.value) for o in obs]
    
    if not values:
        values = [random.uniform(90, 140) for _ in range(30)]
    
    avg = sum(values) / len(values)
    minimum = min(values)
    maximum = max(values)
    
    # Calcular tiempo en rango
    in_range = sum(1 for v in values if 70 <= v <= 180)
    below_range = sum(1 for v in values if v < 70)
    above_range = sum(1 for v in values if v > 180)
    
    pct_in_range = (in_range / len(values)) * 100
    
    return {
        "title": f"Reporte Mensual de Glucosa - {date.strftime('%B %Y')}",
        "source": f"glucose_report_{num}",
        "content": f"""REPORTE MENSUAL DE MONITOREO DE GLUCOSA
Periodo: {start.strftime('%d/%m/%Y')} - {date.strftime('%d/%m/%Y')}
Paciente: Alexander (demo-alex)
Generado: {date.strftime('%d de %B de %Y')}

═══════════════════════════════════════════════════════════════

📊 ESTADÍSTICAS GENERALES

Total de mediciones: {len(values)}
Promedio general: {avg:.1f} mg/dL
Desviación estándar: {(sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5:.1f} mg/dL

Valor mínimo: {minimum:.1f} mg/dL
Valor máximo: {maximum:.1f} mg/dL
Rango: {maximum - minimum:.1f} mg/dL

═══════════════════════════════════════════════════════════════

📈 TIEMPO EN RANGO (Target: 70-180 mg/dL)

{'█' * int(pct_in_range / 2)} {pct_in_range:.1f}% EN RANGO
{'▓' * int((below_range / len(values) * 100) / 2)} {(below_range / len(values) * 100):.1f}% BAJO
{'░' * int((above_range / len(values) * 100) / 2)} {(above_range / len(values) * 100):.1f}% ALTO

Desglose:
  < 70 mg/dL  (Hipoglucemia):  {below_range} mediciones ({(below_range / len(values) * 100):.1f}%)
  70-180 mg/dL (Objetivo):     {in_range} mediciones ({pct_in_range:.1f}%)
  > 180 mg/dL (Hiperglucemia): {above_range} mediciones ({(above_range / len(values) * 100):.1f}%)

═══════════════════════════════════════════════════════════════

📅 ANÁLISIS POR MOMENTO DEL DÍA

Ayunas (6-8 AM):
  Promedio: {random.uniform(95, 130):.1f} mg/dL
  {'✓ Dentro de meta (80-130)' if random.random() > 0.3 else '⚠ Por encima de meta'}

Postdesayuno (2h):
  Promedio: {random.uniform(110, 160):.1f} mg/dL
  {'✓ Controlado' if random.random() > 0.4 else '⚠ Elevado'}

Precomida:
  Promedio: {random.uniform(100, 145):.1f} mg/dL

Postcomida (2h):
  Promedio: {random.uniform(120, 180):.1f} mg/dL
  {'✓ Dentro de meta (<180)' if random.random() > 0.3 else '⚠ Ocasionalmente >180'}

Precena:
  Promedio: {random.uniform(95, 135):.1f} mg/dL

Nocturno (3 AM):
  {'No se realizaron mediciones' if random.random() > 0.8 else f'Promedio: {random.uniform(90, 120):.1f} mg/dL'}

═══════════════════════════════════════════════════════════════

🎯 EVALUACIÓN DE CONTROL

Control glucémico: {'EXCELENTE' if pct_in_range > 80 else 'BUENO' if pct_in_range > 70 else 'REGULAR' if pct_in_range > 60 else 'REQUIERE MEJORA'}

Variabilidad glucémica: {'Baja (deseable)' if (maximum - minimum) < 80 else 'Moderada' if (maximum - minimum) < 120 else 'Alta (revisar causas)'}

Adherencia al monitoreo: {'Excelente' if len(values) > 25 else 'Buena' if len(values) > 20 else 'Regular (incrementar frecuencia)'}

═══════════════════════════════════════════════════════════════

💡 OBSERVACIONES Y RECOMENDACIONES

{f'✓ El {pct_in_range:.0f}% del tiempo en rango objetivo es excelente.' if pct_in_range > 75 else f'⚠ Solo {pct_in_range:.0f}% del tiempo en rango. Meta: >70%'}

{f'⚠ {below_range} episodios de hipoglucemia. Revisar dosis y horarios de medicación.' if below_range > 3 else '✓ Sin episodios significativos de hipoglucemia.'}

{f'⚠ {above_range} episodios de hiperglucemia. Revisar adherencia a dieta y medicación.' if above_range > 8 else '✓ Hiperglucemias bien controladas.'}

{'📉 Tendencia a la mejoría respecto al mes anterior.' if random.random() > 0.5 else '📊 Valores similares al mes previo, mantener plan actual.'}

ACCIONES SUGERIDAS:
1. {f'Intensificar monitoreo en horarios con mayor variabilidad' if (maximum - minimum) > 100 else 'Mantener frecuencia actual de monitoreo'}
2. {'Revisar tamaño de porciones en comidas' if above_range > 8 else 'Continuar con plan alimenticio actual'}
3. {'Considerar ajuste de medicación en próxima consulta' if pct_in_range < 70 else 'Mantener esquema actual de medicación'}
4. Próxima revisión en 30 días

═══════════════════════════════════════════════════════════════

Este reporte fue generado automáticamente basado en las mediciones
registradas. Consulte con su médico para interpretación personalizada.

Fecha de generación: {date.strftime('%Y-%m-%d %H:%M')}
"""
    }

# ============================================================================
# GENERADOR PRINCIPAL
# ============================================================================

def generate_all_documents():
    """Generar todos los documentos para 5 años"""
    user = get_user()
    print(f"\n🏥 Generando historial médico completo para: {user.username}")
    print(f"📅 Periodo: 5 años (1,825 días)")
    print("=" * 80)
    
    documents_created = 0
    documents_exists = 0
    
    # ========== LABORATORIOS ==========
    print("\n📋 GENERANDO LABORATORIOS...")
    
    # Panel Lipídico - cada 6 meses (10 documentos)
    for i in range(10):
        days_ago = i * 180 + random.randint(0, 30)
        date = get_date(days_ago)
        doc_data = generate_panel_lipidico(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # HbA1c - cada 3 meses (20 documentos)
    for i in range(20):
        days_ago = i * 90 + random.randint(0, 15)
        date = get_date(days_ago)
        doc_data = generate_hba1c(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # Panel Metabólico - cada 3 meses (20 documentos)
    for i in range(20):
        days_ago = i * 90 + random.randint(5, 25)
        date = get_date(days_ago)
        doc_data = generate_panel_metabolico(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # ========== CONSULTAS ==========
    print("\n👨‍⚕️ GENERANDO CONSULTAS MÉDICAS...")
    
    # Consultas de control - cada 3 meses (20 documentos)
    for i in range(20):
        days_ago = i * 90 + random.randint(10, 30)
        date = get_date(days_ago)
        doc_data = generate_consulta_control(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # Consultas de nutrición - cada 5 meses (12 documentos)
    for i in range(12):
        days_ago = i * 150 + random.randint(20, 40)
        date = get_date(days_ago)
        doc_data = generate_consulta_nutricion(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # ========== PRESCRIPCIONES ==========
    print("\n💊 GENERANDO PRESCRIPCIONES...")
    
    # Metformina - cada 3 meses (20 documentos)
    for i in range(20):
        days_ago = i * 90 + random.randint(0, 10)
        date = get_date(days_ago)
        doc_data = generate_prescripcion_metformina(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # ========== REPORTES ==========
    print("\n📊 GENERANDO REPORTES MENSUALES...")
    
    # Reportes de glucosa - cada mes (60 documentos)
    for i in range(60):
        days_ago = i * 30 + random.randint(0, 5)
        date = get_date(days_ago)
        doc_data = generate_reporte_mensual_glucosa(date, i + 1)
        doc, created = Document.objects.get_or_create(
            user=user,
            title=doc_data['title'],
            defaults={'source': doc_data['source'], 'content': doc_data['content']}
        )
        if created:
            documents_created += 1
            print(f"  ✓ {doc_data['title']}")
        else:
            documents_exists += 1
    
    # ========== RESUMEN ==========
    print("\n" + "=" * 80)
    print("✅ GENERACIÓN COMPLETADA")
    print("=" * 80)
    print(f"📄 Documentos creados: {documents_created}")
    print(f"📄 Documentos existentes (omitidos): {documents_exists}")
    print(f"📄 Total en base de datos: {Document.objects.filter(user=user).count()}")
    print()
    print("🔄 Próximo paso: Indexar documentos en RAG")
    print("   Ejecutar: python manage.py reindex_documents")
    print()

if __name__ == '__main__':
    generate_all_documents()

