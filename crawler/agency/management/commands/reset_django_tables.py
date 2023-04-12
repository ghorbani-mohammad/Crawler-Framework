from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Drop django tables and ageny, pagestructure, \
        agencycrawlreport tables by Mohammad Ghorbani"

    def handle(self, *_args, **_options):
        cursor = connection.cursor()
        cursor.execute(
            """drop table auth_group, auth_group_permissions, \
                auth_permission, auth_user, auth_user_groups, auth_user_user_permissions, \
                agency_agency, agency_agencypagestructure, \
                agency_crawlreport, django_admin_log, django_content_type, \
                django_migrations, django_session CASCADE"""
        )
