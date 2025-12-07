import os
import random
from datetime import datetime
from faker import Faker

fake = Faker('es_ES')

CONDITIONS = [
    "Diabetes Tipo 2",
    "Hipertensión Arterial",
    "Obesidad Grado 1",
    "Dislipidemia",
    "Lumbago Crónico"
]

SOAP_TEMPLATES = [
    """FECHA: {date}
PACIENTE: Alexander Doe
MOTIVO DE CONSULTA: Control rutinario {condition}

SUBJETIVO:
Paciente de {age} años acude a control. Refiere {symptom}.
Nivel de estrés: {stress}/10. 
Adherencia a medicación: {adherence}.
Cambios en dieta: {diet_changes}.

OBJETIVO:
Peso: {weight} kg
TA: {bp} mmHg
FC: {hr} lpm
Examen físico: {physical_exam}

ANÁLISIS:
{condition} {status}.
Riesgo cardiovascular: {cv_risk}.

PLAN:
1. Continuar con medicación actual.
2. Ajustar dieta: reducir carbohidratos y sal.
3. Actividad física: caminar 30 min diarios.
4. Control en 6 meses con laboratorios nuevos.

Firma:
Dr. {doctor_name}
Matrícula: {license}
""",
    """FECHA: {date}
URGENCIA
PACIENTE: Alexander Doe
MOTIVO: {symptom_acute}

SUBJETIVO:
Paciente refiere inicio de síntomas hace 48hs. Dolor intensidad 7/10.

OBJETIVO:
TA: {bp} mmHg
Temp: 37.5 C
SatO2: 98%

ANÁLISIS:
Cuadro compatible con infección viral estacional. Se descartan complicaciones mayores.

PLAN:
1. Reposo 48hs.
2. Paracetamol 500mg c/8hs si dolor/fiebre.
3. Hidratación abundante.

Firma:
Dr. {doctor_name}
Matrícula: {license}
"""
]

def generate_soap_note(filepath, date, age):
    is_routine = random.random() > 0.2
    
    if is_routine:
        template = SOAP_TEMPLATES[0]
        cond = random.choice(CONDITIONS) if age > 40 else "Control General"
        symptom = random.choice(["sentirse bien", "fatiga ocasional", "sed aumentada", "dolor de espalda leve"])
        bp = f"{random.randint(120, 145)}/{random.randint(75, 95)}" if age > 40 else "115/75"
        weight = 90 + random.randint(-2, 5) if age > 40 else 78
        content = template.format(
            date=date,
            condition=cond,
            age=age,
            symptom=symptom,
            stress=random.randint(3, 8),
            adherence=random.choice(["Buena", "Regular", "Mala"]),
            diet_changes=random.choice(["No", "Intentando reducir harinas", "Comiendo fuera seguido"]),
            weight=weight,
            bp=bp,
            hr=random.randint(65, 85),
            physical_exam="Abdomen blando, depresible, no doloroso. Ruidos cardiacos normales.",
            status="estable" if random.random() > 0.3 else "mal controlado",
            cv_risk="Moderado" if age > 45 else "Bajo",
            doctor_name=fake.name(),
            license=random.randint(10000, 99999)
        )
    else:
        template = SOAP_TEMPLATES[1]
        content = template.format(
            date=date,
            symptom_acute=random.choice(["Fiebre y dolor corporal", "Dolor lumbar agudo", "Cefalea intensa"]),
            bp=f"{random.randint(130, 150)}/{random.randint(80, 100)}",
            doctor_name=fake.name(),
            license=random.randint(10000, 99999)
        )

    with open(filepath, 'w') as f:
        f.write(content)

def main():
    out_dir = 'sample_data/full_history/notes'
    os.makedirs(out_dir, exist_ok=True)
    
    birth_year = 1975
    # Generate ~2 notes per year since 2010
    for year in range(2010, 2026):
        for i in range(random.randint(1, 3)):
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_obj = datetime(year, month, day)
            age = year - birth_year
            fname = os.path.join(out_dir, f"consult_{year}_{month:02d}_{day:02d}.txt")
            generate_soap_note(fname, date_obj.strftime("%Y-%m-%d"), age)
            print(f"Generated {fname}")

if __name__ == "__main__":
    main()

