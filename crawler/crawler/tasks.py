from __future__ import absolute_import, unicode_literals
import redis, json, time, telegram, traceback

from django.conf import settings
from django.utils import timezone
from celery.utils.log import get_task_logger

from agency import utils
from .celery import crawler
from crawler.settings import BOT_API_KEY
from agency import models as age_models
from agency import serializer as age_serializer
from agency.crawler_engine import CrawlerEngine


logger = get_task_logger(__name__)

redis_news = redis.StrictRedis(host="crawler_redis", port=6379, db=0)
Exporter_API_URI = f"http://{settings.SERVER_IP}:8888/crawler/news"
Exporter_API_headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.17.1",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Host": f"{settings.SERVER_IP}:8888",
    "Accept-Encoding": "gzip, deflate",
    "Content-Length": "2796",
    "Connection": "keep-alive",
    "cache-control": "no-cache",
}


def check_must_crawl(page):
    now = timezone.localtime()
    reports = age_models.Report.objects.filter(
        page=page.id, status=age_models.Report.PENDING
    )
    if reports.count() == 0:
        crawl(page)
    else:
        last_report = reports.last()
        if (
            int((now - last_report.created_at).total_seconds() / (60))
            >= page.crawl_interval
        ):
            reports.update(status=age_models.Report.FAILED)
        if (
            int((now - last_report.created_at).total_seconds() / (3600))
            >= page.crawl_interval
        ):
            last_report.status = age_models.Report.FAILED
            last_report.save()
            crawl(page)


@crawler.task(name="check_agencies")
def check():
    logger.info("check_agencies started")
    agencies = age_models.Agency.objects.filter(status=True).values_list(
        "id", flat=True
    )
    pages = (
        age_models.Page.objects.filter(agency__in=agencies)
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
    age_models.Log.objects.create(
        page=page,
        description=description,
        url=url,
        phase=age_models.Log.SENDING,
        error=e,
    )


def crawl(page):
    logger.info(f"---> Page {page.url} must be crawled")
    serializer = age_serializer.PageSerializer(page)
    page_crawl.delay(serializer.data)


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
        logger.info("---> Exporter is locked")
        return
    redis_news.set(settings.REDIS_EXPORTER_LOCK_KEY, 1, 60 * 60 * 2)
    bot = telegram.Bot(token=BOT_API_KEY)  # this bot variable should not removed
    pages = age_models.Page.objects.all()

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
