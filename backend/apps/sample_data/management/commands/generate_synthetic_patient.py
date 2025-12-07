from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Tuple

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.lifecore.models import Observation, TimelineEvent, Document, DocumentChunk
from apps.lifecore.embedding import chunk_text, text_to_embedding
from apps.lifecore.vectorstore_faiss import FaissVectorStore


def daterange(start: datetime, end: datetime, step_days: int):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=step_days)


class Command(BaseCommand):
    help = 'Genera datos sintéticos de 5 años para un usuario: biometría, estilo de vida, medicación/eventos, entrevistas y labs.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default='demo-alex')
        parser.add_argument('--years', type=int, default=5)
        parser.add_argument('--disease', type=str, default='diabetes_progression')

    def handle(self, *args, **options):
        username: str = options['user']
        years: int = int(options['years'])
        disease: str = options['disease']
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username)

        end = datetime.utcnow()
        start = end - timedelta(days=365 * years)

        random.seed(42)

        # Baselines para una progresión leve de diabetes
        glucose_base = 95.0
        weight_base = 78.0
        sbp_base = 125.0
        dbp_base = 80.0
        ldl_base = 130.0
        hdl_base = 45.0
        trig_base = 160.0

        # Medicaciones/eventos
        metformin_start = start + timedelta(days=365 * 3)
        statin_start = start + timedelta(days=365 * 2)

        # Observaciones semanales: glucosa, PA, peso
        for dt in daterange(start, end, 7):
            delta_years = (dt - start).days / 365.0
            # Tendencias
            glucose = glucose_base + 8 * delta_years + random.uniform(-5, 5)
            weight = weight_base + 2.0 * delta_years + random.uniform(-1.5, 1.5)
            sbp = sbp_base + 3 * delta_years + random.uniform(-6, 6)
            dbp = dbp_base + 2 * delta_years + random.uniform(-5, 5)

            if dt >= metformin_start:
                glucose -= 10.0  # efecto de metformina
            if dt >= statin_start:
                ldl_base -= 0.02  # leve reducción sostenida

            Observation.objects.create(user=user, code='glucose', value=round(glucose, 1), unit='mg/dL', taken_at=dt, source='synthetic')
            Observation.objects.create(user=user, code='weight', value=round(weight, 1), unit='kg', taken_at=dt, source='synthetic')
            Observation.objects.create(user=user, code='blood_pressure_systolic', value=round(sbp, 0), unit='mmHg', taken_at=dt, source='synthetic')
            Observation.objects.create(user=user, code='blood_pressure_diastolic', value=round(dbp, 0), unit='mmHg', taken_at=dt, source='synthetic')

        # Observaciones mensuales: lípidos
        cur = start
        while cur <= end:
            delta_years = (cur - start).days / 365.0
            ldl = max(70.0, ldl_base - 5 * delta_years + random.uniform(-10, 10))
            hdl = hdl_base + random.uniform(-4, 4)
            trig = trig_base + random.uniform(-30, 30)
            Observation.objects.create(user=user, code='ldl', value=round(ldl, 1), unit='mg/dL', taken_at=cur, source='synthetic')
            Observation.objects.create(user=user, code='hdl', value=round(hdl, 1), unit='mg/dL', taken_at=cur, source='synthetic')
            Observation.objects.create(user=user, code='triglycerides', value=round(trig, 1), unit='mg/dL', taken_at=cur, source='synthetic')
            cur += timedelta(days=30)

        # Estilo de vida diario: pasos, sueño, ánimo
        for dt in daterange(start, end, 1):
            steps = int(7000 + 500 * random.uniform(-2, 2))
            sleep_h = max(4.0, min(9.5, 7.2 + random.uniform(-1.2, 1.2)))
            mood = max(2.0, min(9.0, 6.5 + random.uniform(-2.0, 2.0)))
            Observation.objects.create(user=user, code='steps', value=steps, unit='count', taken_at=dt, source='synthetic')
            Observation.objects.create(user=user, code='sleep_hours', value=round(sleep_h, 2), unit='hours', taken_at=dt, source='synthetic')
            Observation.objects.create(user=user, code='mood', value=round(mood, 1), unit='', taken_at=dt, source='synthetic')

        # Eventos y medicación
        TimelineEvent.objects.create(user=user, kind='medication.start', payload={'drug': 'metformin'}, occurred_at=metformin_start)
        TimelineEvent.objects.create(user=user, kind='medication.start', payload={'drug': 'atorvastatin'}, occurred_at=statin_start)

        # Documentos: entrevistas y labs
        interview = (
            "Entrevista médica anual: El paciente reporta cambios en la dieta, incremento leve de peso, "
            "y adherencia parcial a metformina desde el último año. Meta: mejorar control glucémico."
        )
        labs = (
            "Resultados de laboratorio (extracto): HbA1c 6.8% (2023-05-10); Glucosa en ayunas 112 mg/dL; "
            "Colesterol LDL 118 mg/dL; HDL 46 mg/dL; Triglicéridos 170 mg/dL."
        )
        for title, content in [("Entrevista anual", interview), ("Laboratorio anual", labs)]:
            doc = Document.objects.create(user=user, title=title, content=content, source='synthetic')
            parts = chunk_text(content)
            for i, part in enumerate(parts):
                emb = text_to_embedding(part)
                DocumentChunk.objects.create(user=user, document=doc, chunk_index=i, text=part, embedding=emb)

        # Construir índice FAISS
        if FaissVectorStore.is_available():
            FaissVectorStore(user.id).build()

        self.stdout.write(self.style.SUCCESS(f"Datos sintéticos generados para {username}"))


