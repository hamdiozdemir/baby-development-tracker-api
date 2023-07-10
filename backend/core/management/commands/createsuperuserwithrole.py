from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a superuser with an additional field "role"'

    def add_arguments(self, parser):
        parser.add_argument('--username', '-u', type=str, required=True, help='Specifies the username for the superuser')
        parser.add_argument('--email', '-e', type=str, required=True, help='Specifies the email for the superuser')
        parser.add_argument('--password', '-p', type=str, required=True, help='Specifies the password for the superuser')
        parser.add_argument('--role', '-r', type=str, required=True, help='Specifies the role for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']
        role = options['role']

        try:
            User.objects.create_superuser(username=username, email=email, password=password, role=role)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        except Exception as e:
            raise CommandError(f'Error creating superuser: {e}')
