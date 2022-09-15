from __future__ import absolute_import, unicode_literals
import os

from logging.config import dictConfig
from django.conf import settings
from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

crawler = Celery("crawler")
crawler.config_from_object("django.conf:settings")
crawler.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@setup_logging.connect
def config_loggers(*args, **kwags):
    dictConfig(settings.LOGGING)


MINUTE = 60

crawler.conf.beat_schedule = {
    "check-agencies-300-seconds": {
        "task": "check_agencies",
        "schedule": 5 * MINUTE,
    },
    "redis-exporter-180-seconds": {
        "task": "redis_exporter",
        "schedule": 3 * MINUTE,
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
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "count_daily_news": {
        "task": "count_daily_news",
        "schedule": crontab(minute=0, hour=0),
    },
}
