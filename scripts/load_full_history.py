import os
import json
import django
from datetime import datetime
from pathlib import Path

# Setup Django
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.lifecore.models import Observation, Document, DocumentChunk, Condition, TimelineEvent
from apps.lifecore.treatment_models import Treatment
from apps.lifecore.vectorstore_faiss import FaissVectorStore
from apps.lifecore.views import _index_document

User = get_user_model()

BASE_DATA_DIR = Path('sample_data/full_history')
if not BASE_DATA_DIR.exists():
    # Try finding it relative to project root if running from inside scripts/
    BASE_DATA_DIR = Path(__file__).resolve().parents[1] / 'sample_data/full_history'


def create_synthetic_user():
    username = "alexander_synthetic"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("demo123")
        user.save()
        print(f"Created user: {username}")
    else:
        print(f"User {username} already exists")
    return user

def load_biometrics(user):
    print("Loading biometrics...")
    vitals_path = BASE_DATA_DIR / 'biometrics/vitals.json'
    if not vitals_path.exists():
        print("Vitals file not found")
        return

    with open(vitals_path) as f:
        data = json.load(f)

    # Observations
    count = 0
    for key in ['weight', 'glucose', 'systolic_bp', 'diastolic_bp']:
        records = data.get(key, [])
        for rec in records:
            Observation.objects.create(
                user=user,
                code=key,
                value=rec['value'],
                unit=rec['unit'],
                taken_at=datetime.fromisoformat(rec['date']),
                source='synthetic_history'
            )
            count += 1
    print(f"Loaded {count} biometric observations")
    
    # Wearables
    wear_path = BASE_DATA_DIR / 'biometrics/wearables.json'
    if wear_path.exists():
        with open(wear_path) as f:
            wdata = json.load(f)
        steps = wdata.get('steps', [])
        # Bulk create for speed
        objs = [
            Observation(
                user=user,
                code='steps',
                value=rec['value'],
                unit='steps',
                taken_at=datetime.fromisoformat(rec['date']),
                source='wearable_device'
            ) for rec in steps
        ]
        Observation.objects.bulk_create(objs)
        print(f"Loaded {len(objs)} wearable records")

def load_documents(user):
    print("Loading documents...")
    # PDFs
    doc_dir = BASE_DATA_DIR / 'documents'
    if doc_dir.exists():
        for f in doc_dir.glob('*.pdf'):
            # Create Document record
            # In a real app we'd upload file, here we just reference path or fake content
            # We'll extract text from PDF or just use a placeholder text for indexing since we lack OCR here
            doc = Document.objects.create(
                user=user,
                title=f.name,
                content=f"Reporte de laboratorio escaneado: {f.name}. Contiene valores de Glucosa, Colesterol, Hemograma...",
                source='lab_import'
            )
            # Index it
            _index_document(doc)
            print(f"Indexed PDF: {f.name}")
            
    # Notes (TXT)
    notes_dir = BASE_DATA_DIR / 'notes'
    if notes_dir.exists():
        for f in notes_dir.glob('*.txt'):
            content = f.read_text()
            # Extract date from filename or content
            try:
                date_str = f.stem.split('consult_')[1].replace('_', '-')
                created_at = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                created_at = datetime.now()
                
            doc = Document.objects.create(
                user=user,
                title=f"Nota de Consulta - {created_at.date()}",
                content=content,
                source='medical_record'
            )
            # Hack: update created_at manually
            doc.created_at = created_at
            doc.save()
            
            # También crear TimelineEvent para esta consulta
            TimelineEvent.objects.create(
                user=user,
                kind='medical_encounter',
                category='consultation',
                payload={'title': f"Consulta Médica - {created_at.date()}", 'reason': 'Control rutinario'},
                occurred_at=created_at,
                data_summary={'source_doc_id': doc.id}
            )

            _index_document(doc)
            print(f"Indexed Note & Event: {f.name}")

def create_timeline_events(user):
    print("Creating timeline events...")
    # Birth
    TimelineEvent.objects.create(
        user=user,
        kind='medical_history',
        category='life_event',
        payload={'description': 'Nacimiento'},
        occurred_at=datetime(1975, 5, 20),
        data_summary={'weight': '3.2kg', 'location': 'Hospital Central'}
    )
    
    # Diagnosis
    TimelineEvent.objects.create(
        user=user,
        kind='diagnosis',
        category='clinical',
        payload={'condition': 'Diabetes Mellitus Tipo 2', 'code': 'E11'},
        occurred_at=datetime(2017, 3, 15),
        severity='chronic'
    )
    
    # Medication Start
    TimelineEvent.objects.create(
        user=user,
        kind='treatment_start',
        category='treatment',
        payload={'medication': 'Metformina', 'dosage': '500mg'},
        occurred_at=datetime(2017, 3, 20)
    )

def main():
    user = create_synthetic_user()
    
    # Clear old data for this user to avoid dups
    Observation.objects.filter(user=user).delete()
    Document.objects.filter(user=user).delete()
    TimelineEvent.objects.filter(user=user).delete()
    
    load_biometrics(user)
    load_documents(user)
    create_timeline_events(user)
    
    # Build FAISS Index
    print("Building FAISS index...")
    FaissVectorStore(user.id).build()
    print("FAISS index built successfully.")
    
    print("Full history generation complete.")

if __name__ == "__main__":
    main()

