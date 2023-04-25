import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

application = get_wsgi_application()

try:
    import redis
    from agency.models import Page, Report

    print(
        f"***** {Page.objects.filter(lock=True).update(lock=False)} update: lock=False *****"
    )
    print(
        f"***** {Report.objects.filter(status='pending').update(status='failed')} update: \
            status=failed *****"
    )
    redis_news = redis.StrictRedis(host="crawler-redis", port=6379, db=0)
except Exception:
    pass
