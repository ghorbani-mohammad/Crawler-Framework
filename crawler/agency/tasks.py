from __future__ import absolute_import, unicode_literals
import redis, json, time, telegram, traceback

from django.conf import settings
from django.utils import timezone
from celery.utils.log import get_task_logger
from crawler.celery import crawler

from . import utils, serializer, models
from .crawler_engine import CrawlerEngine
from crawler.settings import BOT_API_KEY
from notification import models as not_models
from notification import utils as not_utils


logger = get_task_logger(__name__)

redis_news = redis.StrictRedis(host="crawler_redis", port=6379, db=0)


@crawler.task(name="remove_old_reports")
def remove_old_reports():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    models.Report.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="remove_old_logs")
def remove_old_logs():
    before_time = timezone.localtime() - timezone.timedelta(days=7)
    models.Log.objects.filter(created_at__lte=before_time).delete()[0]


@crawler.task(name="reset_locks")
def reset_locks():
    models.Page.objects.update(lock=False)


@crawler.task(name="send_log_to_telegram")
def send_log_to_telegram(message):
    bot = not_models.TelegramBot.objects.first()
    account = not_models.TelegramAccount.objects.first()
    not_utils.telegram_bot_sendtext(bot.telegram_token, account.chat_id, message)


def check_must_crawl(page):
    now = timezone.localtime()
    reports = models.Report.objects.filter(page=page.id, status=models.Report.PENDING)
    if reports.count() == 0:
        crawl(page)
    else:
        last_report = reports.last()
        if (
            int((now - last_report.created_at).total_seconds() / (60))
            >= page.crawl_interval
        ):
            reports.update(status=models.Report.FAILED)
        if (
            int((now - last_report.created_at).total_seconds() / (3600))
            >= page.crawl_interval
        ):
            last_report.status = models.Report.FAILED
            last_report.save()
            crawl(page)


@crawler.task(name="check_agencies")
def check():
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


def register_log(description, e, page, url):
    logger.error(traceback.format_exc())
    models.Log.objects.create(
        page=page,
        description=description,
        url=url,
        phase=models.Log.SENDING,
        error=e,
    )


def crawl(page):
    page_serializer = serializer.PageSerializer(page)
    page_crawl.delay(page_serializer.data)


@crawler.task(name="page_crawl")
def page_crawl(page_structure):
    CrawlerEngine(page_structure)


@crawler.task(name="page_crawl_repetitive")
def page_crawl_repetitive(page_structure):
    CrawlerEngine(page_structure, repetitive=True)


@crawler.task(name="redis_exporter")
def redis_exporter():
    lock = redis_news.get(settings.REDIS_EXPORTER_LOCK_KEY)
    if lock:
        logger.error("---> Exporter is locked")
        return
    redis_news.set(settings.REDIS_EXPORTER_LOCK_KEY, 1)
    bot = telegram.Bot(token=BOT_API_KEY)  # this bot variable should not removed
    pages = models.Page.objects.all()

    for key in redis_news.scan_iter("*"):
        if key.decode("utf-8") == settings.REDIS_EXPORTER_LOCK_KEY:
            continue
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
                e = "page is None"
                register_log(desc, e, page, data["link"])
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
                exec(temp_code)
                time.sleep(2)
            except Exception as e:
                desc = f"code was: {temp_code}"
                register_log(desc, e, page, data["link"])
        except Exception as e:
            desc = f"key was: {key.decode('utf-8')}"
            register_log(desc, e, page, data["link"])
        finally:
            redis_news.delete(key)
    redis_news.delete(settings.REDIS_EXPORTER_LOCK_KEY)
