from django.core.management import call_command


def seed_demo():
    call_command('generate_synthetic_patient', user='demo-alex', years=5)
    call_command('generate_synthetic_patient', user='demo-eve', years=5)


