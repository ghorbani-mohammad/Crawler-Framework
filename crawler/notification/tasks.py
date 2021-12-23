import datetime
from django.db.models import Sum
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from agency import models as age_models
from . import models
from . import utils


@periodic_task(
    run_every=(crontab(minute='0', hour='0')),
    name="count_daily_news",
)
def count_daily_news():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    new_links = (
        age_models.CrawlReport.objects.filter(created_at__gt=yesterday).aggregate(
            Sum('new_links')
        )['new_links__sum']
        or 0
    )

    message = f'Today we saw {new_links} new links'
    bot = models.TelegramBot.objects.first()
    account = models.TelegramAccount.objects.first()
    utils.telegram_bot_sendtext(bot.telegram_token, account.chat_id, message)
