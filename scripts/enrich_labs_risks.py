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
from apps.lifecore.models import Observation, TimelineEvent, Document, Condition
from apps.lifecore.treatment_models import Treatment
from apps.lifecore.views import _index_document
from apps.lifecore.vectorstore_faiss import FaissVectorStore

User = get_user_model()

def enrich_labs_risks():
    print("Iniciando enriquecimiento: Labs Avanzados y Farmacología...")
    
    try:
        user = User.objects.get(username="alexander_synthetic")
    except User.DoesNotExist:
        print("Usuario 'alexander_synthetic' no encontrado.")
        return

    print(f"Usuario: {user.username}")
    
    today = datetime.now()
    
    # 1. LABORATORIOS RECIENTES (Hace 2 días)
    # Perfil Lipídico Alterado (Dislipidemia)
    lab_date = today - timedelta(days=2)
    
    labs = [
        ('cholesterol_total', 240, 'mg/dL'), # High
        ('cholesterol_ldl', 160, 'mg/dL'),   # High
        ('cholesterol_hdl', 35, 'mg/dL'),    # Low
        ('triglycerides', 180, 'mg/dL'),     # High
        ('glucose', 105, 'mg/dL'),           # Borderline
        ('hba1c', 5.9, '%'),                 # Prediabetes range
        ('systolic_bp', 135, 'mmHg'),        # Elevated
        ('diastolic_bp', 85, 'mmHg')
    ]
    
    for code, val, unit in labs:
        Observation.objects.create(
            user=user,
            code=code,
            value=val,
            unit=unit,
            taken_at=lab_date,
            source='lab_import_auto'
        )
        
    # Evento de Lab
    TimelineEvent.objects.create(
        user=user,
        kind="lab_result",
        category="lab",
        payload={
            "title": "Perfil Metabólico y Lipídico",
            "description": "Resultados muestran hipercolesterolemia y glucosa limítrofe.",
            "source": "Laboratorio Central"
        },
        occurred_at=lab_date,
        related_conditions=['dyslipidemia', 'diabetes']
    )
    print("Labs recientes inyectados (Colesterol Alto).")

    # 2. MEDICAMENTOS ACTIVOS (Para probar interacciones)
    # Warfarina (Anticoagulante) - Alto riesgo de interacción
    t1 = Treatment.objects.create(
        user=user,
        name="Warfarina",
        medication_type="Anticoagulante",
        dosage="5mg",
        frequency="Diaria",
        start_date=today - timedelta(days=30),
        status="active",
        condition="Prevención ACV"
    )
    TimelineEvent.objects.create(
        user=user,
        kind="treatment.start",
        category="treatment",
        payload={"title": "Inicio Warfarina", "description": "Anticoagulante oral."},
        occurred_at=today - timedelta(days=30),
        related_conditions=['cardio']
    )

    # Atorvastatina (Para el colesterol)
    t2 = Treatment.objects.create(
        user=user,
        name="Atorvastatina",
        medication_type="Estatina",
        dosage="20mg",
        frequency="Noche",
        start_date=today - timedelta(days=2), # Empezó tras el lab
        status="active",
        condition="Dislipidemia"
    )
    TimelineEvent.objects.create(
        user=user,
        kind="treatment.start",
        category="treatment",
        payload={"title": "Inicio Atorvastatina", "description": "Manejo de colesterol alto."},
        occurred_at=today - timedelta(days=2),
        related_conditions=['dyslipidemia']
    )
    
    print("Tratamientos activos inyectados: Warfarina, Atorvastatina.")
    
    # Reconstruir índice por si acaso
    FaissVectorStore(user.id).build()
    print("Listo. Pruebas habilitadas: analyze_lab_panels, check_drug_interactions.")

if __name__ == "__main__":
    enrich_labs_risks()

