from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Change type of news_meta_structure from jsonb to json"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute(
            """ALTER TABLE agency_agencypagestructure ALTER COLUMN news_meta_structure TYPE json"""
        )
