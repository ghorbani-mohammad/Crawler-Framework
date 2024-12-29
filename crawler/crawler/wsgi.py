import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

application = get_wsgi_application()

try:
    from agency.models import Page, Report
    from agency.tasks import clear_all_redis_locks

    print(
        f"***** {Page.objects.filter(lock=True).update(lock=False)} update: lock=False *****"
    )
    print(
        f"***** {Report.objects.filter(status='pending').update(status='failed')} update: \
            status=failed *****"
    )
    clear_all_redis_locks()
    print("***** All redis locks cleared *****")
except ImportError:
    pass
