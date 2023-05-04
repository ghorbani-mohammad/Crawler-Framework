from __future__ import absolute_import, unicode_literals
import json
import time
import traceback
import redis
import telegram

from django.conf import settings
from django.utils import timezone
from celery.utils.log import get_task_logger
from notification import utils as not_utils
from notification import models as not_models
from reusable.other import only_one_concurrency

from crawler.celery import crawler
from .crawler_engine import CrawlerEngine
from . import utils, serializer, models


logger = get_task_logger(__name__)
MINUTE = 60
TASKS_TIMEOUT = 10 * MINUTE
redis_news = redis.StrictRedis(host="crawler-redis", port=6379, db=0)


@crawler.task(name="remove_old_reports")
def remove_old_reports():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    _count = models.Report.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="remove_old_logs")
def remove_old_logs():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    _count = models.Log.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="reset_locks")
def reset_locks():
    models.Page.objects.update(lock=False)


@crawler.task(name="send_log_to_telegram")
def send_log_to_telegram(message):
    bot = not_models.TelegramBot.objects.first()
    account = not_models.TelegramAccount.objects.first()
    not_utils.telegram_bot_send_text(bot.telegram_token, account.chat_id, message)


def check_must_crawl(page):
    now = timezone.localtime()
    reports = models.Report.objects.filter(page=page.id, status=models.Report.PENDING)
    if reports.count() == 0:
        crawl(page)
    else:
        last_report = reports.last()
        diff_in_secs = (now - last_report.created_at).total_seconds()
        print(diff_in_secs)
        logger.info(diff_in_secs)
        diff_in_min = int(diff_in_secs / (60))
        logger.info(diff_in_min)
        print(diff_in_min)
        if diff_in_min >= page.crawl_interval:
            if last_report.status == models.Report.PENDING:
                last_report.status = models.Report.FAILED
            crawl(page)


@crawler.task(name="check_agencies")
def check_agencies():
    logger.info("check_agencies started")
    agencies = models.Agency.objects.filter(status=True).values_list("id", flat=True)
    pages = (
        models.Page.objects.filter(agency__in=agencies)
        .filter(lock=False)
        .filter(status=True)
    )
    now = timezone.localtime()
    for page in pages:
        if page.last_crawl is None:
            check_must_crawl(page)
        else:
            diff_minute = int((now - page.last_crawl).total_seconds() / (60))
            if diff_minute >= page.crawl_interval:
                check_must_crawl(page)


def register_log(description, error, page, url):
    logger.error(traceback.format_exc())
    models.Log.objects.create(
        page=page,
        description=description,
        url=url,
        phase=models.Log.SENDING,
        error=error,
    )


def crawl(page):
    page_crawl.delay(serializer.PageSerializer(page).data)


@crawler.task(name="page_crawl")
@only_one_concurrency(key="page_crawl", timeout=TASKS_TIMEOUT)
def page_crawl(page_structure):
    CrawlerEngine(page_structure)


@crawler.task(name="page_crawl_repetitive")
@only_one_concurrency(key="page_crawl_repetitive", timeout=TASKS_TIMEOUT)
def page_crawl_repetitive(page_structure):
    CrawlerEngine(page_structure, repetitive=True)


@crawler.task(name="redis_exporter")
@only_one_concurrency(key="redis_exporter", timeout=TASKS_TIMEOUT)
def redis_exporter():
    # this bot variable should not removed
    bot = telegram.Bot(token=settings.BOT_API_KEY)  # pylint: disable=unused-variable
    pages = models.Page.objects.all()
    for key in redis_news.scan_iter("links_*"):
        data = redis_news.get(key)
        if data is None:
            redis_news.delete(key)
            continue
        data = data.decode("utf-8")
        page = None
        try:
            data = json.loads(data)
            page = pages.filter(pk=data["page_id"], status=True).first()
            if page is None:
                desc = f"data is: {data}"
                error = "page is None"
                register_log(desc, error, page, data["link"])
                redis_news.delete(key)
                continue
            data["iv_link"] = f"https://t.me/iv?url={data['link']}&rhash={page.iv_code}"
            temp_code = utils.CODE.format(page.message_code)
            try:
                temp_code = (
                    temp_code
                    + "\n"
                    + "bot.send_message(chat_id=page.telegram_channel, text=message)"
                )
                exec(temp_code)  # pylint: disable=exec-used
                time.sleep(4)
            except Exception as error:  # pylint: disable=broad-except
                desc = f"code was: {temp_code}"
                register_log(desc, error, page, data["link"])
        except Exception as error:  # pylint: disable=broad-except
            desc = f"key was: {key.decode('utf-8')}"
            register_log(desc, error, page, data["link"])
        finally:
            redis_news.delete(key)


@crawler.task()
def test_error():
    logger.error("Test Error!")
    raise Exception("hi")
