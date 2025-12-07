import os
import sys
import django
from datetime import datetime, timedelta
from pathlib import Path
import random

# Setup Django
sys.path.append(str(Path(__file__).resolve().parents[1] / 'backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.lifecore.models import Document, TimelineEvent, Condition, EventCondition
from apps.lifecore.views import _index_document
from apps.lifecore.vectorstore_faiss import FaissVectorStore

User = get_user_model()

def enrich_history():
    print("Iniciando enriquecimiento de historial clínico...")
    
    try:
        user = User.objects.get(username="alexander_synthetic")
    except User.DoesNotExist:
        print("Usuario 'alexander_synthetic' no encontrado. Asegúrate de haber corrido load_full_history.py")
        return

    print(f"Usuario encontrado: {user.username} (ID: {user.id})")

    # 1. ANTECEDENTES PERSONALES Y FAMILIARES (Historia Clínica Inicial)
    # Fecha: 20 años después del nacimiento (1975 + 20 = 1995)
    initial_date = datetime(1995, 6, 15)
    
    initial_history_content = """
    HISTORIA CLÍNICA INICIAL - ADMISIÓN
    
    Fecha: 15 de Junio de 1995
    Paciente: Alexander Doe
    Edad: 20 años
    
    ANTECEDENTES FAMILIARES:
    - Padre: Diagnosticado con Diabetes Tipo 2 a los 50 años. Hipertensión controlada.
    - Madre: Sana, sin antecedentes cardiovasculares relevantes. Fallecida abuela materna por ACV.
    - Hermanos: Uno, sano.
    
    ANTECEDENTES PERSONALES PATOLÓGICOS:
    - Infancia: Varicela a los 5 años, Sarampión leve.
    - Quirúrgicos: Apendicectomía a los 12 años sin complicaciones.
    - Alergias: Penicilina (reacción cutánea leve).
    - Traumatismos: Fractura de radio distal derecho a los 10 años (jugando fútbol).
    
    HÁBITOS:
    - Tabaquismo: Niega.
    - Alcohol: Ocasional social.
    - Actividad Física: Moderada (fútbol fines de semana).
    
    EXAMEN FÍSICO INICIAL:
    - Normopeso, presión arterial 110/70 mmHg.
    - Sin hallazgos patológicos al momento.
    
    PLAN:
    - Control anual preventivo debido a carga genética diabética paterna.
    """
    
    # Crear Documento
    doc_initial = Document.objects.create(
        user=user,
        title="Historia Clínica Inicial - Antecedentes",
        content=initial_history_content,
        created_at=initial_date,
        source="medical_record_legacy"
    )
    # Ajustar fecha real
    Document.objects.filter(id=doc_initial.id).update(created_at=initial_date)
    _index_document(doc_initial)
    
    # Crear Evento Timeline
    TimelineEvent.objects.create(
        user=user,
        kind="medical_history",
        category="consultation",
        payload={
            "title": "Apertura de Historia Clínica",
            "description": "Registro de antecedentes familiares y personales. Carga genética positiva para Diabetes.",
            "source": "Dr. Smith (Generalista)"
        },
        occurred_at=initial_date,
        data_summary={'source_doc_id': doc_initial.id},
        related_conditions=['diabetes'] # Vinculamos preventivamente
    )
    print("Creada Historia Clínica Inicial (1995)")


    # 2. EVOLUCIÓN DE SÍNTOMAS (Diabetes)
    # Vamos a simular una evolución desde el diagnóstico (asumimos ~2015 por los datos previos) hasta hoy.
    
    # Nota 1: Inicio de síntomas (2014)
    date_symptoms = datetime(2014, 11, 10)
    symptoms_content = """
    CONSULTA DE MEDICINA INTERNA
    Fecha: 10/11/2014
    
    Motivo de consulta: Polidipsia y poliuria.
    
    Enfermedad Actual:
    Paciente de 39 años refiere cuadro de 2 meses de evolución caracterizado por sed excesiva (polidipsia) y aumento en la frecuencia urinaria (poliuria), incluso nocturna.
    Refiere además pérdida de peso no intencional de 3kg en el último mes a pesar de aumento del apetito.
    Se siente fatigado por las tardes.
    
    Impresión Diagnóstica:
    Sindrome metabólico a descartar Diabetes Mellitus de debut.
    
    Plan:
    - Solicitar HbA1c, Glucosa en ayunas, Perfil lipídico.
    """
    
    doc_sym = Document.objects.create(
        user=user,
        title="Consulta - Inicio de Síntomas",
        content=symptoms_content,
        created_at=date_symptoms,
        source="medical_record"
    )
    Document.objects.filter(id=doc_sym.id).update(created_at=date_symptoms)
    _index_document(doc_sym)
    
    TimelineEvent.objects.create(
        user=user,
        kind="medical_encounter",
        category="consultation",
        payload={
            "title": "Consulta por Síntomas Metabólicos",
            "description": "Paciente refiere polidipsia, poliuria y fatiga. Sospecha de diabetes.",
            "reason": "Sintomas nuevos"
        },
        occurred_at=date_symptoms,
        data_summary={'source_doc_id': doc_sym.id},
        related_conditions=['diabetes']
    )
    
    # Nota 2: Evolución positiva tras tratamiento (2016)
    date_improvement = datetime(2016, 5, 20)
    improv_content = """
    CONTROL DIABETES MELLITUS
    Fecha: 20/05/2016
    
    Evolución:
    Paciente acude a control trimestral. Refiere buena adherencia a Metformina 850mg.
    Ha iniciado caminatas diarias de 30 minutos.
    Niega síntomas de hipoglucemia. La poliuria ha desaparecido completamente.
    Peso estable.
    
    Laboratorio reciente:
    - HbA1c: 6.8% (Previa 7.5%) - MEJORÍA
    
    Comentario:
    Buena respuesta al tratamiento farmacológico y cambios en estilo de vida.
    Continuar igual.
    """
    
    doc_imp = Document.objects.create(
        user=user,
        title="Control Diabetes - Evolución Positiva",
        content=improv_content,
        created_at=date_improvement,
        source="medical_record"
    )
    Document.objects.filter(id=doc_imp.id).update(created_at=date_improvement)
    _index_document(doc_imp)
    
    TimelineEvent.objects.create(
        user=user,
        kind="medical_encounter",
        category="consultation",
        payload={
            "title": "Control Diabetes - Mejoría",
            "description": "HbA1c desciende a 6.8%. Síntomas remitidos. Buena adherencia.",
        },
        occurred_at=date_improvement,
        data_summary={'source_doc_id': doc_imp.id},
        related_conditions=['diabetes']
    )

    # Nota 3: Recaída leve / Ajuste (2022)
    date_relapse = datetime(2022, 12, 10)
    relapse_content = """
    CONTROL ANUAL
    Fecha: 10/12/2022
    
    Evolución:
    Paciente admite haber descuidado la dieta durante las festividades y últimos meses por estrés laboral.
    Ha ganado 4kg.
    Refiere visión borrosa ocasional.
    
    Examen Físico:
    PA 135/85 mmHg. BMI 29.
    
    Plan:
    - Reforzar dieta.
    - Interconsulta oftalmología (fondo de ojo).
    - Se añade Sitagliptina si no mejora en 3 meses.
    """
    
    doc_rel = Document.objects.create(
        user=user,
        title="Control - Recaída Leve",
        content=relapse_content,
        created_at=date_relapse,
        source="medical_record"
    )
    Document.objects.filter(id=doc_rel.id).update(created_at=date_relapse)
    _index_document(doc_rel)
    
    TimelineEvent.objects.create(
        user=user,
        kind="medical_encounter",
        category="consultation",
        payload={
            "title": "Control Diabetes - Descuido Dietético",
            "description": "Aumento de peso y estrés. Visión borrosa ocasional. Se refuerza dieta.",
        },
        occurred_at=date_relapse,
        data_summary={'source_doc_id': doc_rel.id},
        related_conditions=['diabetes', 'obesity', 'hypertension']
    )

    print("Generadas notas de evolución (2014, 2016, 2022)")
    
    # Reconstruir índice vectorial para asegurar búsqueda
    print("Actualizando índice vectorial...")
    FaissVectorStore(user.id).build()
    print("Enriquecimiento completado.")

if __name__ == "__main__":
    enrich_history()

