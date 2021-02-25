from __future__ import absolute_import, unicode_literals

import logging, datetime, redis, json
import telegram, time

from .celery import crawler
from agency.models import Agency, Page, Report, Log
from agency.serializer import AgencyPageStructureSerializer
from agency.crawler_engine import CrawlerEngine


# TODO: configs must be dynamic
redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)


def check_must_crawl(page):
    now = datetime.datetime.now()
    x = Report.objects.filter(page=page.id, status='pending')
    if x.count() == 0:
        crawl(page)
    else:
        last_report = x.last()
        if int((now - last_report.created_at).total_seconds()/(60)) >= page.crawl_interval:
            x.update(status='failed')
            crawl(page)


@crawler.task(name='check_agencies')
def check():
    agencies = Agency.objects.filter(status= True).values_list('id', flat= True)
    pages = Page.objects.filter(agency__in=agencies).filter(lock=False).filter(status=True)
    now = datetime.datetime.now()
    for page in pages:
        if page.last_crawl is None:
            check_must_crawl(page)
        else:
            diff_hour = int((now - page.last_crawl).total_seconds()/(60))
            if diff_hour >= page.crawl_interval:
                check_must_crawl(page)


def crawl(page):
    logging.info("---> Page %s must be crawled", page.url)
    serializer = AgencyPageStructureSerializer(page)
    page_crawl.delay(serializer.data)


@crawler.task(name='page_crawl')
def page_crawl(page_structure):
    logging.info("---> Page crawling is started")
    CrawlerEngine(page_structure)


@crawler.task(name='page_crawl_repetitive')
def page_crawl_repetitive(page_structure):
    logging.info("---> Page crawling is started")
    CrawlerEngine(page_structure, repetitive= True)


@crawler.task(name='redis_exporter')
def redis_exporter():
    API_KEY = '1395437640:AAFZ1mkohxundOSBwBek1B8SPnApO4nIIMo'
    bot = telegram.Bot(token=API_KEY)
    pages = Page.objects.all()

    for key in redis_news.scan_iter("*"):
        data = (redis_news.get(key).decode('utf-8'))
        page = None
        try:
            data = json.loads(data)
            page = pages.filter(pk=data['page_id'], status=True).first()
            if page is None:
                Log.objects.create(
                    page=page, url=data['link'], phase=Log.SENDING, error='page is None',
                    description='data is: {}'.format(data)
                )
                redis_news.delete(key)
                continue
            data['iv_link'] = "https://t.me/iv?url={}&rhash={}".format(data['link'], page.iv_code)
            temp_code = """
{0}
            """
            temp_code = temp_code.format(page.message_code)
            try:
                temp_code = temp_code + '\n' + 'bot.send_message(chat_id=page.telegram_channel, text=message)'
                exec(temp_code)
                time.sleep(3)
            except Exception as e:
                Log.objects.create(
                    page=page, url=data['link'], phase=Log.SENDING, error=str(e),
                    description='code was: {}'.format(temp_code)
                )
        except Exception as e:
            Log.objects.create(
                page=page, url=data['link'], phase=Log.SENDING, error=str(e),
                description='key was: {}'.format(key.decode('utf-8'))
            )
        finally:
            redis_news.delete(key)
