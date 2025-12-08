import os
import sys
import django
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.models import Observation, Document, TimelineEvent
from django.contrib.auth.models import User
from apps.lifecore.vectorstore_faiss import FaissVectorStore

def enrich_lifestyle_data(user_id=8):
    print(f"Enriching lifestyle data for User ID: {user_id}")
    user = User.objects.get(id=user_id)
    
    # 1. Generate Sleep Data (Last 30 days)
    print("Generating sleep logs...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    current = start_date
    while current <= end_date:
        # Sleep Hours (6.5 - 8.5)
        hours = round(random.uniform(6.5, 8.5), 1)
        # Sleep Score (70-95)
        score = int(random.uniform(70, 95))
        # REM Sleep (15-25%)
        rem = int(random.uniform(15, 25))
        
        Observation.objects.create(user=user, code='sleep_hours', value=hours, unit='h', taken_at=current, source='Oura Ring')
        Observation.objects.create(user=user, code='sleep_score', value=score, unit='score', taken_at=current, source='Oura Ring')
        Observation.objects.create(user=user, code='rem_sleep', value=rem, unit='%', taken_at=current, source='Oura Ring')
        
        current += timedelta(days=1)

    # 2. Generate Advanced Wearable Metrics (VO2 Max, HRV)
    print("Generating advanced wearable metrics...")
    # VO2 Max (Monthly)
    for i in range(12):
        date = end_date - timedelta(days=30*i)
        val = 42 + (i * 0.2) # Improving slightly over time (reversed logic here, actually getting worse if we go back in time, improving forward)
        # Let's make it improve: 40 a year ago, 45 now
        val = 40 + ((12-i)/12 * 5) + random.uniform(-1, 1)
        Observation.objects.create(user=user, code='vo2_max', value=round(val, 1), unit='mL/kg/min', taken_at=date, source='Apple Watch')
        
    # HRV (Daily last 7 days)
    for i in range(7):
        date = end_date - timedelta(days=i)
        val = int(random.uniform(40, 65))
        Observation.objects.create(user=user, code='hrv', value=val, unit='ms', taken_at=date, source='Oura Ring')
        
        # Resting HR
        rhr = int(random.uniform(55, 65))
        Observation.objects.create(user=user, code='resting_hr', value=rhr, unit='bpm', taken_at=date, source='Oura Ring')

    # 3. Generate Nutritional Log (Document)
    print("Generating nutritional logs...")
    nutri_text = """
    Diario Nutricional - Semana del 10/2025
    
    Lunes:
    - Desayuno: Avena con frutas, café negro. (400 kcal)
    - Almuerzo: Ensalada César con pollo, sin crutones. (600 kcal)
    - Cena: Pescado al horno con vegetales. (500 kcal)
    Observaciones: Buen consumo de agua. Evité azúcares refinados.
    
    Martes:
    - Desayuno: Huevos revueltos, tostada integral.
    - Almuerzo: Lentejas con arroz.
    - Cena: Yogur griego con nueces.
    Observaciones: Sentí un poco de ansiedad por dulce a la tarde. Comí una manzana.
    
    Plan General: Dieta Mediterránea baja en carbohidratos simples. Objetivo: Reducción de grasa visceral.
    """
    
    doc = Document.objects.create(
        user=user,
        title="Diario Nutricional - Oct 2025",
        content=nutri_text,
        created_at=datetime.now() - timedelta(days=2)
    )
    
    # Create Event for the doc
    TimelineEvent.objects.create(
        user=user,
        kind='medical_encounter', # Reuse kind for now or add 'lifestyle_log'
        category='lifestyle',
        payload={'title': 'Diario Nutricional', 'description': 'Registro semanal de dieta'},
        occurred_at=doc.created_at,
        data_summary={'source_doc_id': doc.id}
    )
    
    # Re-index to find this doc
    print("Re-indexing vector store...")
    FaissVectorStore(user.id).build()

    print("Lifestyle data enrichment complete.")

if __name__ == '__main__':
    enrich_lifestyle_data()

