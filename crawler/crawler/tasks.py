from __future__ import absolute_import, unicode_literals
from bs4 import BeautifulSoup
from dateutil import relativedelta
import logging, datetime, redis, json, time, telegram
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.conf import settings
from .celery import crawler
from celery.task.schedules import crontab
from celery.utils.log import get_task_logger

from .celery import crawler
from app.settings import BOT_API_KEY
from agency.models import Agency, Page, Report, Log
from agency.serializer import AgencyPageStructureSerializer
from agency.crawler_engine import CrawlerEngine


logger = get_task_logger(__name__)

# TODO: configs must be dynamic
redis_news = redis.StrictRedis(host="crawler_redis", port=6379, db=0)
Exporter_API_URI = f"http://{settings.SERVER_IP}:8888/crawler/news"
Exporter_API_headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.17.1",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Postman-Token": "4b465a23-1b28-4b86-981d-67ccf94dda70,4beba7c1-fd77-4b44-bb14-2ea60fbfa590",
    "Host": f"{settings.SERVER_IP}:8888",
    "Accept-Encoding": "gzip, deflate",
    "Content-Length": "2796",
    "Connection": "keep-alive",
    "cache-control": "no-cache",
}


def check_must_crawl(page):
    now = datetime.datetime.now()
    x = Report.objects.filter(page=page.id, status="pending")
    if x.count() == 0:
        crawl(page)
    else:
        last_report = x.last()
        if (
            int((now - last_report.created_at).total_seconds() / (60))
            >= page.crawl_interval
        ):
            x.update(status="failed")
        if (
            int((now - last_report.created_at).total_seconds() / (3600))
            >= page.crawl_interval
        ):
            last_report.status = "failed"
            last_report.save()
            crawl(page)


@crawler.task(name="check_agencies")
def check():
    logger.info("check_agencies started")
    agencies = Agency.objects.filter(status=True).values_list("id", flat=True)
    pages = (
        Page.objects.filter(agency__in=agencies).filter(lock=False).filter(status=True)
    )
    now = datetime.datetime.now()
    for page in pages:
        if page.last_crawl is None:
            check_must_crawl(page)
        else:
            diff_minute = int((now - page.last_crawl).total_seconds() / (60))
            if diff_minute >= page.crawl_interval:
                check_must_crawl(page)


def crawl(page):
    logging.info(f"---> Page {page.url} must be crawled")
    serializer = AgencyPageStructureSerializer(page)
    page_crawl.delay(serializer.data)


@crawler.task(name="page_crawl")
def page_crawl(page_structure):
    logging.info("---> Page crawling is started")
    CrawlerEngine(page_structure)


@crawler.task(name="page_crawl_repetitive")
def page_crawl_repetitive(page_structure):
    logging.info("---> Page crawling is started")
    CrawlerEngine(page_structure, repetitive=True)


@crawler.task(name="redis_exporter")
def redis_exporter():
    lock = redis_news.get(settings.REDIS_EXPORTER_LOCK_KEY)
    if lock:
        logging.info("---> Exporter is locked")
        print("---> Exporter is locked")
        return
    redis_news.set(settings.REDIS_EXPORTER_LOCK_KEY, 1, 60 * 60 * 2)
    bot = telegram.Bot(token=BOT_API_KEY) # this bot variable should not removed
    pages = Page.objects.all()

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
                Log.objects.create(
                    page=page,
                    url=data["link"],
                    phase=Log.SENDING,
                    error="page is None",
                    description=f"data is: {data}",
                )
                redis_news.delete(key)
                continue
            data["iv_link"] = f"https://t.me/iv?url={data['link']}&rhash={page.iv_code}"
            temp_code = """
{0}
            """
            temp_code = temp_code.format(page.message_code)
            try:
                temp_code = (
                    temp_code
                    + "\n"
                    + "bot.send_message(chat_id=page.telegram_channel, text=message)"
                )
                exec(temp_code)
                time.sleep(3)
            except Exception as e:
                Log.objects.create(
                    page=page,
                    url=data["link"],
                    phase=Log.SENDING,
                    error=str(e),
                    description=f"code was: {temp_code}",
                )
        except Exception as e:
            Log.objects.create(
                page=page,
                url=data["link"],
                phase=Log.SENDING,
                error=str(e),
                description=f"key was: {key.decode('utf-8')}",
            )
        finally:
            redis_news.delete(key)
    redis_news.delete(settings.REDIS_EXPORTER_LOCK_KEY)

@crawler.task(name="remove_obsolete_reports")
def remove_obsolete_reports():
    now = datetime.datetime.now()
    past_month = now - relativedelta.relativedelta(months=1)
    Report.objects.filter(created_at__lte=past_month).delete()


@crawler.task(
    run_every=(crontab(minute=0, hour=0)), name="reset_locks", ignore_result=True
)
def reset_locks():
    Page.objects.update(lock=False)
