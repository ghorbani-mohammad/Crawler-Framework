from django.utils import timezone
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab

from . import models as age_models


logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute=0, hour=0)), name="remove_old_reports", ignore_result=True
)
def remove_old_reports():
    past = timezone.datetime.today() - timezone.timedelta(days=10)
    print('Deleted reports: {}'.format(age_models.Report.objects.filter(created_at__lte=past).delete()[0]))


@periodic_task(
    run_every=(crontab(minute=0, hour=0)), name="remove_old_logs", ignore_result=True
)
def remove_old_logs():
    past = timezone.datetime.today() - timezone.timedelta(days=10)
    print('Deleted reports: {}'.format(age_models.Report.objects.filter(created_at__lte=past).delete()[0]))


@periodic_task(
    run_every=(crontab(minute=0, hour=0)), name="reset_locks", ignore_result=True
)
def reset_locks():
    age_models.Page.objects.update(lock=False)
