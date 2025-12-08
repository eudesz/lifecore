import os
import sys
import django
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.lifecore.models import Observation, Document, TimelineEvent, Condition, EventCondition
from apps.lifecore.treatment_models import Treatment, TreatmentLog
from apps.lifecore.vectorstore_faiss import FaissVectorStore
from scripts.sync_graph import sync_graph  # Reusing our graph sync logic


def ensure_laura_conditions() -> None:
    """
    Ensure we have Condition objects for the key clinical concepts in Laura's case.
    This makes the knowledge graph richer and more readable.
    """
    condition_defs = [
        ("lupus", "Lupus Eritematoso Sistémico", "#f97316"),
        ("pancreatitis", "Pancreatitis", "#f97373"),
        ("proteinuria", "Proteinuria Significativa", "#22c55e"),
        ("antiphospholipid_syndrome", "Síndrome Antifosfolípido (SAF)", "#eab308"),
        ("thrombosis_risk", "Riesgo Trombótico Elevado", "#0ea5e9"),
        ("seguimiento_general", "Seguimiento General", "#64748b"),
        ("anemia_cronica", "Anemia Crónica", "#ef4444"),
        ("renal_impairment", "Compromiso Renal Crónico", "#22c55e"),
        ("metabolic_risk", "Riesgo Metabólico", "#6366f1"),
    ]
    for slug, name, color in condition_defs:
        Condition.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "color": color},
        )


def link_event_conditions(event: TimelineEvent, slugs: list[str]) -> None:
    """
    Link a TimelineEvent with Condition objects using EventCondition so
    the Neo4j graph can represent these relationships.
    """
    for slug in slugs or []:
        cond = Condition.objects.filter(slug=slug).first()
        if not cond:
            continue
        EventCondition.objects.get_or_create(event=event, condition=cond)


def generate_longitudinal_history(user: User, base_date: datetime, lupus_onset: datetime, years: int = 50):
    """
    Generate a long synthetic history (labs + checkups) so Laura has ~years of data
    for SQL, vector search and the knowledge graph.
    """
    print(f"Generating ~{years} years of background data for Laura...")
    start_date = base_date - timedelta(days=365 * years)
    current = start_date
    processed_years = set()

    # Simple baseline trajectories (they will drift slightly over décadas)
    weight = 40.0  # kg at infancy / adolescence range
    systolic_bp = 100.0
    glucose = 85.0
    steps = 8000.0
    resting_hr = 75.0
    sleep_hours = 8.0
    sleep_score = 80.0

    while current <= base_date:
        # Small random walk around trends
        weight += random.uniform(-0.3, 0.4)
        systolic_bp += random.uniform(-1.5, 1.5)
        glucose += random.uniform(-1.0, 1.2)
        steps += random.uniform(-500, 500)
        resting_hr += random.uniform(-1.0, 1.0)
        sleep_hours += random.uniform(-0.3, 0.3)
        sleep_score += random.uniform(-2.0, 2.0)

        # Clamp to reasonable ranges
        weight = max(40.0, min(80.0, weight))
        systolic_bp = max(90.0, min(160.0, systolic_bp))
        glucose = max(70.0, min(180.0, glucose))
        steps = max(1000.0, min(20000.0, steps))
        resting_hr = max(50.0, min(110.0, resting_hr))
        sleep_hours = max(4.0, min(10.0, sleep_hours))
        sleep_score = max(40.0, min(100.0, sleep_score))

        # Structured observations every few months
        Observation.objects.create(
            user=user,
            code='weight',
            value=round(weight, 1),
            unit='kg',
            taken_at=current,
            source='SyntheticHistory',
        )
        Observation.objects.create(
            user=user,
            code='systolic_bp',
            value=round(systolic_bp, 0),
            unit='mmHg',
            taken_at=current,
            source='SyntheticHistory',
        )
        Observation.objects.create(
            user=user,
            code='glucose',
            value=round(glucose, 0),
            unit='mg/dL',
            taken_at=current,
            source='SyntheticHistory',
        )

        # Aggregated wearables snapshot for the period (average values)
        Observation.objects.create(
            user=user,
            code='steps_daily_avg',
            value=round(steps, 0),
            unit='steps/day',
            taken_at=current,
            source='Wearable',
        )
        Observation.objects.create(
            user=user,
            code='resting_hr',
            value=round(resting_hr, 0),
            unit='bpm',
            taken_at=current,
            source='Wearable',
        )
        Observation.objects.create(
            user=user,
            code='sleep_hours',
            value=round(sleep_hours, 1),
            unit='h/night',
            taken_at=current,
            source='Wearable',
        )
        Observation.objects.create(
            user=user,
            code='sleep_score',
            value=round(sleep_score, 0),
            unit='score',
            taken_at=current,
            source='Wearable',
        )

        # Once per year check (independent of loop step) - we use a set to track years processed
        if current.year not in processed_years:
            processed_years.add(current.year)
            year_label = current.year
            
            # Place the annual checkup roughly in January-February
            checkup_date = datetime(year_label, 1, 15) + timedelta(days=random.randint(0, 45))
            # Ensure we don't go beyond base_date
            if checkup_date > base_date:
                checkup_date = base_date

            note_text = f"""
            CONTROL ANUAL DE LAURA - AÑO {year_label}

            Resumen general:
            - Seguimiento longitudinal de peso, presión arterial y glucosa.
            - Sin eventos agudos relevantes registrados en este período.
            - Se recomienda continuar controles periódicos según protocolo pediátrico/reumatológico.
            """
            doc = Document.objects.create(
                user=user,
                title=f'Control Anual - {year_label}',
                content=note_text,
                created_at=checkup_date,
            )
            ev = TimelineEvent.objects.create(
                user=user,
                kind='medical_encounter',
                category='consultation',
                payload={
                    'title': f'Control Anual {year_label}',
                    'description': 'Visita de control general con registro de signos vitales y labs básicos.',
                },
                occurred_at=checkup_date,
                data_summary={'source_doc_id': doc.id, 'role': 'result'},
                related_conditions=['seguimiento_general'],
            )
            link_event_conditions(ev, ['seguimiento_general'])

            # Annual comprehensive lab panel (blood, urine, stool) — may repeat 2–3 times algunos años
            is_post_lupus = checkup_date >= lupus_onset
            num_panels = 1
            if is_post_lupus and random.random() < 0.4:
                num_panels = random.choice([2, 3])

            for i in range(num_panels):
                # Pequeño desplazamiento dentro del año
                panel_date = checkup_date + timedelta(days=i * 90) # spaced out more
                if panel_date > base_date: break

                # --- Hemograma ---
                hb = random.uniform(12.0, 14.0) - (0.8 if is_post_lupus and random.random() < 0.3 else 0.0)
                rbc = random.uniform(4.2, 4.8)
                hct = hb * 3  # aproximación
                wbc = random.uniform(5.0, 9.0) + (1.5 if is_post_lupus and random.random() < 0.3 else 0.0)
                platelets = random.uniform(180, 380)

                # --- Metabólico / Renal / Hepático / Lipídico ---
                glucose_lab = random.uniform(75, 105) + (15 if random.random() < 0.15 else 0.0)
                calcium = random.uniform(8.6, 10.0)
                sodium = random.uniform(136, 144)
                potassium = random.uniform(3.6, 4.9)
                chloride = random.uniform(98, 105)
                bicarb = random.uniform(24, 28)

                bun = random.uniform(8, 18)
                creat = random.uniform(0.7, 1.0) + (0.3 if is_post_lupus and random.random() < 0.2 else 0.0)
                egfr = random.uniform(80, 110) - (20 if creat > 1.2 else 0.0)
                uric = random.uniform(3.0, 6.0)

                alt = random.uniform(10, 40)
                ast = random.uniform(10, 40)
                alp = random.uniform(60, 130)
                bili_total = random.uniform(0.4, 1.1)
                bili_direct = random.uniform(0.1, 0.3)
                albumin = random.uniform(3.6, 4.8)
                total_protein = random.uniform(6.3, 7.8)

                chol_total = random.uniform(160, 220)
                hdl = random.uniform(45, 65)
                ldl = random.uniform(80, 140)
                trig = random.uniform(90, 190)

                tsh = random.uniform(0.6, 3.5)
                t4_free = random.uniform(0.9, 1.8)
                t3_total = random.uniform(90, 180)

                pt = random.uniform(11.0, 13.5)
                inr = random.uniform(0.9, 1.2)
                aptt = random.uniform(26, 35)

                crp = random.uniform(0.3, 3.0) + (10.0 if is_post_lupus and panel_date.year % 4 == 0 else 0.0)
                esr = random.uniform(5, 18) + (15 if is_post_lupus and random.random() < 0.3 else 0.0)

                urine_protein = random.uniform(0.05, 0.15) + (0.5 if is_post_lupus and panel_date.year % 6 == 0 else 0.0)
                stool_occult = 0 if random.random() > 0.9 else 1

                # Persist observations (resumen, no todo el CBC diferencial para no explotar la BD)
                def obs(code, value, unit):
                    Observation.objects.create(
                        user=user,
                        code=code,
                        value=round(value, 2),
                        unit=unit,
                        taken_at=panel_date,
                        source='AnnualLab',
                    )

                obs('cbc_rbc', rbc, 'mill/mcL')
                obs('cbc_hb', hb, 'g/dL')
                obs('cbc_hct', hct, '%')
                obs('cbc_wbc', wbc, 'x10^9/L')
                obs('cbc_platelets', platelets, '/mcL')

                obs('met_glucose', glucose_lab, 'mg/dL')
                obs('met_calcium', calcium, 'mg/dL')
                obs('met_sodium', sodium, 'mEq/L')
                obs('met_potassium', potassium, 'mEq/L')
                obs('met_chloride', chloride, 'mEq/L')
                obs('met_bicarbonate', bicarb, 'mEq/L')

                obs('bun', bun, 'mg/dL')
                obs('creatinine', creat, 'mg/dL')
                obs('egfr', egfr, 'mL/min')
                obs('uric_acid', uric, 'mg/dL')

                obs('alt', alt, 'U/L')
                obs('ast', ast, 'U/L')
                obs('alp', alp, 'UI/L')
                obs('bilirubin_total', bili_total, 'mg/dL')
                obs('bilirubin_direct', bili_direct, 'mg/dL')
                obs('albumin', albumin, 'g/dL')
                obs('total_protein', total_protein, 'g/dL')

                obs('chol_total', chol_total, 'mg/dL')
                obs('hdl', hdl, 'mg/dL')
                obs('ldl', ldl, 'mg/dL')
                obs('triglycerides', trig, 'mg/dL')

                obs('tsh', tsh, 'mUI/L')
                obs('t4_free', t4_free, 'ng/dL')
                obs('t3_total', t3_total, 'ng/dL')

                obs('pt', pt, 'sec')
                obs('inr', inr, 'ratio')
                obs('aptt', aptt, 'sec')

                obs('crp_highsens', crp, 'mg/L')
                obs('esr', esr, 'mm/hr')

                obs('urine_protein', urine_protein, 'g/24h')
                obs('stool_occult_blood', stool_occult, 'bool')

                # Flags para el resumen y condiciones asociadas
                lab_flags = []
                related = ['seguimiento_general']
                if hb < 11.0:
                    lab_flags.append("anemia")
                    related.append('anemia_cronica')
                if creat > 1.2 or egfr < 60:
                    lab_flags.append("compromiso renal")
                    related.append('renal_impairment')
                if urine_protein > 0.3:
                    lab_flags.append("proteinuria significativa")
                    related.append('proteinuria')
                if crp > 10 or esr > 30:
                    lab_flags.append("inflamación sistémica")
                if chol_total > 220 or trig > 200:
                    lab_flags.append("riesgo metabólico")
                    related.append('metabolic_risk')

                lab_summary = "Panel de laboratorio dentro de parámetros esperados."
                if lab_flags:
                    lab_summary = "Alteraciones relevantes: " + ", ".join(sorted(set(lab_flags))) + "."

                lab_doc = Document.objects.create(
                    user=user,
                    title=f'Panel Laboratorio {year_label} - {i + 1}',
                    content=f"Resumen del laboratorio del año {year_label} (panel {i + 1}).\n\nConclusión clínica: {lab_summary}",
                    created_at=panel_date,
                )
                lab_ev = TimelineEvent.objects.create(
                    user=user,
                    kind='lab_panel.comprehensive',
                    category='lab',
                    payload={
                        'title': f'Panel Lab {year_label} ({i + 1})',
                        'description': lab_summary,
                    },
                    occurred_at=panel_date,
                    data_summary={'source_doc_id': lab_doc.id, 'role': 'result'},
                    related_conditions=list(set(related)),
                )
                link_event_conditions(lab_ev, list(set(related)))

            # Occasional imaging reports tied to abdominal / vascular checks
            if is_post_lupus and year_label % 5 == 0:
                imaging_text = f"""
                ESTUDIO DE IMAGEN - ECO / DOPPLER {year_label}

                Motivo: Control en paciente con LES y riesgo trombótico.
                Hallazgos: Sin trombosis venosa profunda evidente. Órganos abdominales sin lesiones focales significativas.
                Conclusión: Estudio sin hallazgos agudos, continuar seguimiento clínico.
                """
                img_doc = Document.objects.create(
                    user=user,
                    title=f'Estudio de Imagen - Control Vascular {year_label}',
                    content=imaging_text,
                    created_at=current,
                )
                img_ev = TimelineEvent.objects.create(
                    user=user,
                    kind='imaging.control',
                    category='imaging',
                    payload={
                        'title': f'Imagen Control Vascular {year_label}',
                        'description': 'Control ecográfico / doppler en contexto de LES y SAF.',
                    },
                    occurred_at=current,
                    data_summary={'source_doc_id': img_doc.id, 'role': 'result'},
                    related_conditions=['lupus', 'antiphospholipid_syndrome'],
                )
                link_event_conditions(img_ev, ['lupus', 'antiphospholipid_syndrome'])

        # Advance roughly one quarter
        current += timedelta(days=90)

def generate_laura():
    print("Generating case: Laura (SLE Teenager)...")
    
    # 1. Create User
    username = "laura_sle"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("demo123")
        user.save()
        print(f"User created: {username} (ID: {user.id})")
    else:
        print(f"User exists: {username} (ID: {user.id})")
        # Clean cleanup for demo
        TimelineEvent.objects.filter(user=user).delete()
        Document.objects.filter(user=user).delete()
        Observation.objects.filter(user=user).delete()
        Treatment.objects.filter(user=user).delete()

    base_date = datetime.now()

    # 0. Ensure Condition catalog and longitudinal background (50 years de vitals + labs + imagen + wearables)
    ensure_laura_conditions()
    # Placeholder lupus onset; we adjust later once the diagnosis is created, but for labs necesitamos un estimado
    lupus_onset_estimate = base_date - timedelta(days=365 * 3)
    generate_longitudinal_history(user, base_date, lupus_onset=lupus_onset_estimate, years=50)

    # 2. Background (Diagnosis 3 years ago)
    diag_date = base_date - timedelta(days=365 * 3)
    
    diag_event = TimelineEvent.objects.create(
        user=user,
        kind='diagnosis',
        category='diagnosis',
        payload={'title': 'Diagnóstico: Lupus Eritematoso Sistémico (LES)', 'description': 'Debut con rash malar y artritis.'},
        occurred_at=diag_date,
        related_conditions=['lupus', 'sle']
    )
    link_event_conditions(diag_event, ['lupus'])
    
    # Base Treatment
    Treatment.objects.create(
        user=user,
        name="Hidroxicloroquina",
        medication_type="Antimalárico",
        dosage="200mg",
        frequency="Cada 24hs",
        start_date=diag_date,
        status="active",
        condition="Lupus"
    )

    # 3. The Flare-up (Admission - 5 Days ago)
    admit_date = base_date - timedelta(days=5)
    
    # Admission Note
    admit_text = """
    NOTA DE INGRESO - URGENCIAS PEDIÁTRICAS
    Paciente femenina de 16 años con antecedentes de LES diagnosticado hace 3 años.
    Consulta por dolor abdominal severo en epigastrio irradiado a dorso, náuseas y fatiga extrema.
    
    Examen Físico:
    - TA: 110/70, FC: 98 lpm.
    - Abdomen: Dolor a la palpación en epigastrio. RHA disminuidos.
    - Piel: Leve rash en mejillas.
    
    Impresión: Sospecha de brote lúpico. Descartar pancreatitis lúpica vs causa biliar.
    Plan: Solicitar amilasa, lipasa, función renal y perfil autoinmune completo.
    """
    
    doc_admit = Document.objects.create(user=user, title="Ingreso Urgencias - Dolor Abdominal", content=admit_text, created_at=admit_date)
    admit_event = TimelineEvent.objects.create(
        user=user, kind='medical_encounter', category='consultation',
        payload={'title': 'Ingreso Hospitalario', 'description': 'Sospecha brote LES / Pancreatitis'},
        occurred_at=admit_date, data_summary={'source_doc_id': doc_admit.id},
        related_conditions=['lupus', 'pancreatitis']
    )
    link_event_conditions(admit_event, ['lupus', 'pancreatitis'])

    # 4. The Labs (3 Days ago) - Confirming the scenario
    lab_date = base_date - timedelta(days=3)
    
    # Observations (Structured)
    Observation.objects.create(user=user, code='lipase', value=450, unit='U/L', taken_at=lab_date, source='Lab Central', extra={'ref_range': '0-160'})
    Observation.objects.create(user=user, code='amylase', value=200, unit='U/L', taken_at=lab_date, source='Lab Central')
    Observation.objects.create(user=user, code='proteinuria_24h', value=1.5, unit='g/24h', taken_at=lab_date, source='Lab Central', extra={'status': 'High'})
    
    # Lab Report Document (Unstructured details)
    lab_text = """
    REPORTE DE LABORATORIO - INMUNOLOGÍA Y QUÍMICA
    
    Química:
    - Lipasa: 450 U/L (Alto) -> Compatible con Pancreatitis Aguda.
    - Amilasa: 200 U/L.
    
    Orina:
    - Proteinuria significativa: 1.5g en 24hs.
    - Sedimento activo.
    
    Perfil SAF (Síndrome Antifosfolípido):
    - Anticoagulante Lúpico: POSITIVO.
    - Anticuerpos Anticardiolipina IgG/IgM: Títulos moderados a altos.
    
    Conclusión:
    Brote lúpico severo con compromiso pancreático (Pancreatitis) y renal (Nefritis).
    Presencia de marcadores de alto riesgo trombótico (SAF).
    """
    
    doc_lab = Document.objects.create(user=user, title="Resultados Laboratorio - Perfil Inmunológico", content=lab_text, created_at=lab_date)
    lab_event = TimelineEvent.objects.create(
        user=user, kind='lab_result', category='lab',
        payload={'title': 'Confirmación: Pancreatitis y SAF', 'description': 'Lipasa elevada y Anticoagulante Lúpico Positivo'},
        occurred_at=lab_date, data_summary={'source_doc_id': doc_lab.id},
        related_conditions=['pancreatitis', 'antiphospholipid_syndrome', 'proteinuria']
    )
    link_event_conditions(lab_event, ['pancreatitis', 'antiphospholipid_syndrome', 'proteinuria'])

    # 5. The Clinical Dilemma (Yesterday) - Interconsultation Note
    consult_date = base_date - timedelta(days=1)
    
    # Using the specific text provided by the user for rich context
    consult_text = """
    INTERCONSULTA - REUMATOLOGÍA / HEMATOLOGÍA
    
    Situación Clínica:
    Adolescente con LES en brote agudo.
    Hallazgos: Pancreatitis, Proteinuria (1.5g) y Anticuerpos Antifosfolípidos positivos en sangre.
    
    Dilema Terapéutico:
    Se trata de una afección clínica muy grave y poco frecuente en adolescentes. 
    Existe un riesgo elevado de desarrollar un coágulo sanguíneo (trombosis) debido a los anticuerpos SAF y la inflamación sistémica.
    
    Pregunta Clínica:
    ¿Debe recibir una medicación anticoagulante una adolescente con lupus sistémico que desarrolla proteinuria y tiene anticuerpos antifosfolípidos?
    
    Análisis de Evidencia:
    - No existen estudios bibliográficos publicados específicos para esta constelación en adolescentes.
    - La afección es rara; la experiencia individual es limitada.
    - No hay consenso claro en guías clínicas estándar.
    
    Razonamiento:
    El riesgo de trombosis es alto ("constelación de síntomas pro-trombóticos").
    Sin embargo, la pancreatitis y la nefritis pueden aumentar el riesgo de sangrado si se anticoagula agresivamente.
    
    Plan Sugerido:
    1. Iniciar profilaxis antitrombótica (Heparina bajo peso molecular) si no hay contraindicación de sangrado activo.
    2. Monitoreo estricto.
    3. Buscar casos similares en la base de datos del centro médico académico (QuantIA History search).
    """
    
    doc_consult = Document.objects.create(user=user, title="Ateneo Médico - Decisión Anticoagulación", content=consult_text, created_at=consult_date)
    dilemma_event = TimelineEvent.objects.create(
        user=user, kind='medical_encounter', category='consultation',
        payload={'title': 'Dilema: ¿Anticoagular?', 'description': 'Análisis de riesgo trombosis vs sangrado en LES complejo.'},
        occurred_at=consult_date, data_summary={'source_doc_id': doc_consult.id},
        related_conditions=['lupus', 'thrombosis_risk']
    )
    link_event_conditions(dilemma_event, ['lupus', 'thrombosis_risk'])

    # 6. Build Indices
    print("Building Vector Index...")
    FaissVectorStore(user.id).build()
    
    print("Syncing Knowledge Graph...")
    try:
        sync_graph(user.id)
    except Exception as e:
        print(f"Graph sync failed (Neo4j might be down): {e}")

    print("\n=== LAURA CASE GENERATED SUCCESSFULLY ===")
    print(f"User ID: {user.id}")
    print("You can now login as 'laura_sle' or select her in the demo menu.")

if __name__ == '__main__':
    generate_laura()

