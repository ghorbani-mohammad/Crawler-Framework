from django.utils import timezone
from crawler.celery import crawler
from celery.utils.log import get_task_logger

from . import models as age_models
from notification import models as not_models
from notification import utils as not_utils


logger = get_task_logger(__name__)


@crawler.task(name="remove_old_reports")
def remove_old_reports():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    age_models.Report.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="remove_old_logs")
def remove_old_logs():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    age_models.Log.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="reset_locks")
def reset_locks():
    age_models.Page.objects.update(lock=False)


@crawler.task(name="send_log_to_telegram")
def send_log_to_telegram(message):
    bot = not_models.TelegramBot.objects.first()
    account = not_models.TelegramAccount.objects.first()
    not_utils.telegram_bot_sendtext(bot.telegram_token, account.chat_id, message)
