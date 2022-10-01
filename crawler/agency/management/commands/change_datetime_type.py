from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Change type of datetime column from with timezone to without timezone"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute(
            '''ALTER TABLE agency_agency ALTER COLUMN created_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_crawlreport ALTER COLUMN created_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_crawlreport ALTER COLUMN updated_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_agencypagestructure ALTER COLUMN created_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_agency ALTER COLUMN updated_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_agency ALTER COLUMN deleted_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_agencypagestructure ALTER COLUMN updated_at TYPE "timestamp"'''
        )
        cursor.execute(
            '''ALTER TABLE agency_agencypagestructure ALTER COLUMN last_crawl TYPE "timestamp"'''
        )
