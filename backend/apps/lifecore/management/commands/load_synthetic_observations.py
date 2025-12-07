from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from pathlib import Path
import json

from apps.lifecore.models import Observation


class Command(BaseCommand):
    help = 'Carga observaciones sintéticas desde platform/sample_data/observations/*.json'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='ID de usuario destino', required=False)

    def handle(self, *args, **options):
        # Buscar carpeta 'platform' ascendiendo desde este archivo
        p = Path(__file__).resolve()
        platform_dir = None
        for ancestor in p.parents:
            if ancestor.name == 'platform':
                platform_dir = ancestor
                break
        if platform_dir is None:
            self.stdout.write(self.style.ERROR('No se encontró carpeta platform en los ancestros'))
            return
        base = platform_dir / 'sample_data' / 'observations'
        if not base.exists():
            self.stdout.write(self.style.ERROR(f'Directorio no encontrado: {base}'))
            return

        files = list(base.glob('*.json'))
        if not files:
            self.stdout.write(self.style.WARNING('No hay archivos JSON en sample_data/observations'))
            return

        User = get_user_model()
        if options.get('user_id'):
            user = User.objects.get(id=options['user_id'])
        else:
            user, _ = User.objects.get_or_create(username='demo_user')

        total = 0
        for f in files:
            data = json.loads(f.read_text())
            obs = data.get('observations', {})
            for code, series in obs.items():
                for item in series:
                    Observation.objects.create(
                        user=user,
                        code=code,
                        value=float(item['value']),
                        unit=_default_unit(code),
                        taken_at=parse_iso(item['date']),
                        source='synthetic'
                    )
                    total += 1
        self.stdout.write(self.style.SUCCESS(f'Observaciones cargadas: {total}'))


def _default_unit(code: str) -> str:
    mapping = {
        'glucose': 'mg/dl',
        'cholesterol': 'mg/dl',
        'weight': 'kg',
        'blood_pressure_systolic': 'mmHg',
        'blood_pressure_diastolic': 'mmHg',
    }
    return mapping.get(code, '')


def parse_iso(s: str):
    try:
        return timezone.make_aware(timezone.datetime.fromisoformat(s.replace('Z', '+00:00')))
    except Exception:
        return timezone.now()
