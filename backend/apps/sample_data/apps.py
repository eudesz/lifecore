from django.apps import AppConfig


class SampleDataConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'apps.sample_data'
  verbose_name = 'Sample Data'


