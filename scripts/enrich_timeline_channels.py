import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.lifecore.models import TimelineEvent, Document, Observation


def ensure_imaging_and_procedures(user_id: int) -> None:
  """
  Create a few synthetic IMAGING and PROCEDURE events for the given user,
  aligned with existing dates, so the new matrix timeline rows are populated.
  """
  user = User.objects.get(id=user_id)
  print(f"Enriching imaging/procedures for user #{user_id} ({user.username})")

  # Use existing documents / observations to anchor dates
  any_doc = Document.objects.filter(user=user).order_by('created_at').first()
  any_obs = Observation.objects.filter(user=user).order_by('taken_at').first()
  base_date = None
  if any_doc:
    base_date = any_doc.created_at
  elif any_obs:
    base_date = any_obs.taken_at
  else:
    base_date = datetime.now()

  # Avoid duplicates if script re-run
  existing_imaging = TimelineEvent.objects.filter(user=user, category='imaging').count()
  existing_proc = TimelineEvent.objects.filter(user=user, category='procedure').count()

  # IMAGING events
  if existing_imaging < 2:
    d1 = base_date + timedelta(days=60)
    d2 = base_date + timedelta(days=365)
    TimelineEvent.objects.create(
      user=user,
      kind='imaging',
      category='imaging',
      payload={'title': 'Abdominal Ultrasound', 'description': 'Ultrasound to evaluate abdominal pain.'},
      occurred_at=d1,
    )
    TimelineEvent.objects.create(
      user=user,
      kind='imaging',
      category='imaging',
      payload={'title': 'Echocardiogram', 'description': 'Cardiac ultrasound for function assessment.'},
      occurred_at=d2,
    )
    print(f"  Added IMAGING events at {d1.date()} and {d2.date()}")
  else:
    print("  Imaging events already present, skipping.")

  # PROCEDURE events
  if existing_proc < 1:
    d3 = base_date + timedelta(days=180)
    TimelineEvent.objects.create(
      user=user,
      kind='procedure',
      category='procedure',
      payload={'title': 'Minor Procedure', 'description': 'Outpatient minor procedure recorded.'},
      occurred_at=d3,
    )
    print(f"  Added PROCEDURE event at {d3.date()}")
  else:
    print("  Procedure events already present, skipping.")


def main() -> None:
  # Focus on main synthetic/demo users
  for uid in (8, 9):
    try:
      ensure_imaging_and_procedures(uid)
    except User.DoesNotExist:
      print(f"User {uid} does not exist, skipping.")


if __name__ == '__main__':
  main()


