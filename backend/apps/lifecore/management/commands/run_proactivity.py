from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.lifecore.models import Observation, TimelineEvent
import math
from apps.api.flags import is_enabled

class Command(BaseCommand):
    help = 'Run proactivity checks across users and log timeline alerts.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--code', type=str, action='append', default=['glucose'])

    def handle(self, *args, **options):
        if not is_enabled('PROACTIVITY'):
            self.stdout.write(self.style.WARNING('Proactivity disabled by FEATURE_PROACTIVITY flag. Exiting.'))
            return
        days = options['days']
        codes = options['code']
        since = timezone.now() - timezone.timedelta(days=days)
        User = get_user_model()
        users = User.objects.all()
        total_alerts = 0
        for u in users:
            alerts = []
            for code in codes:
                qs = Observation.objects.filter(user=u, code=code, taken_at__gte=since).order_by('taken_at')
                values = [float(o.value) for o in qs]
                if len(values) < 3:
                    continue
                mean = sum(values) / len(values)
                var = sum((v - mean) ** 2 for v in values) / len(values)
                std = math.sqrt(var) if var > 0 else 0.0
                if std > 0:
                    outliers = [i for i, v in enumerate(values) if abs((v - mean) / std) > 2.0]
                    if outliers:
                        alerts.append({'code': code, 'kind': 'outliers', 'count': len(outliers)})
            if alerts:
                TimelineEvent.objects.create(user=u, kind='proactivity.alert', payload={'alerts': alerts}, occurred_at=timezone.now())
                total_alerts += 1
        self.stdout.write(self.style.SUCCESS(f'Proactivity run complete. Users with alerts: {total_alerts}'))
