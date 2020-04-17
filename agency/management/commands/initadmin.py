from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crate a superuser, and allow password to be provided by Mohammad Ghorbani'
    def handle(self, *args, **options):
        User = get_user_model()
        User.objects.create_superuser('army', password='army')

