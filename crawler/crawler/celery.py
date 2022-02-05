from __future__ import absolute_import, unicode_literals
import os

from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

# TODO: redis port and ip and db must be dynamic
crawler = Celery(
    "crawler",
    broker="redis://crawler_redis:6379/10",
    backend="redis://crawler_redis:6379/10",
    include=["crawler.tasks", "agency.tasks"],
)

# Optional configuration, see the application user guide.
crawler.conf.update(result_expires=7200)
crawler.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


crawler.conf.beat_schedule = {
    "check-agencies-300-seconds": {
        "task": "check_agencies",
        "schedule": 5 * 60,
    },
    "redis-exporter-180-seconds": {
        "task": "redis_exporter",
        "schedule": 3 * 60,
    },
    "remove_old_reports": {
        "task": "remove_old_reports",
        "schedule": crontab(minute=0, hour=0),
    },
    "remove_old_logs": {
        "task": "remove_old_logs",
        "schedule": crontab(minute=0, hour=0),
    },
    "reset_locks": {
        "task": "reset_locks",
        "schedule": crontab(hour="*/3"),
    },
    "count_daily_news": {
        "task": "count_daily_news",
        "schedule": crontab(minute=0, hour=0),
    },
}


if __name__ == "__main__":
    crawler.start()
