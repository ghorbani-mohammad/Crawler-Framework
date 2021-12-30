from django.utils import timezone
from crawler.celery import crawler
from celery.utils.log import get_task_logger

from . import models as age_models


logger = get_task_logger(__name__)


@crawler.task(name="remove_old_reports")
def remove_old_reports():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    age_models.Report.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="remove_old_logs")
def remove_old_logs():
    logger.info("hello")
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    age_models.Log.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="reset_locks")
def reset_locks():
    age_models.Page.objects.update(lock=False)
