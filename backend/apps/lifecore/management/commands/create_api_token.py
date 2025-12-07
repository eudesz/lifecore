from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.lifecore.models import ApiClientToken


class Command(BaseCommand):
    help = 'Crea un token de API por usuario'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--scopes', default='read')

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=options['username'])
        token = ApiClientToken.objects.create(user=user, scopes=options['scopes'])
        self.stdout.write(self.style.SUCCESS(f'Token creado: {token.token} para usuario {user.username}'))
