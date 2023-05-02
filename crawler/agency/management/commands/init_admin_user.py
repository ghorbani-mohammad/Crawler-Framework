from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crate a superuser user=admin and pass=test1234"

    def handle(self, *args, **options):
        user_model = get_user_model()
        user_model.objects.create_superuser("admin", password="test1234")
