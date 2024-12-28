import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

application = get_wsgi_application()

try:
    import redis
    from agency.models import Page, Report
    from agency.tasks import clear_all_locks

    print(
        f"***** {Page.objects.filter(lock=True).update(lock=False)} update: lock=False *****"
    )
    print(
        f"***** {Report.objects.filter(status='pending').update(status='failed')} update: \
            status=failed *****"
    )
    clear_all_locks()
    redis_news = redis.StrictRedis(host="crawler-redis", port=6379, db=0)
except ImportError:
    pass
