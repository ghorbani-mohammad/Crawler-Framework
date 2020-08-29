from __future__ import absolute_import, unicode_literals
import requests
from bs4 import BeautifulSoup
import logging, datetime, redis, requests, json


import telegram, time

from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from .celery import crawler
from celery import current_app
from agency.models import Agency, Page, CrawlReport
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer
from agency.crawler_engine import CrawlerEngine


logger = logging.getLogger('django')

# TODO: configs must be dynamic
redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
redis_links = redis.StrictRedis(host='crawler_redis', port=6379, db=1)
Exporter_API_URI = "http://138.201.77.42:8888/crawler/news"
Exporter_API_headers = {
                            'Content-Type': "application/json",
                            'User-Agent': "PostmanRuntime/7.17.1",
                            'Accept': "*/*",
                            'Cache-Control': "no-cache",
                            'Postman-Token': "4b465a23-1b28-4b86-981d-67ccf94dda70,4beba7c1-fd77-4b44-bb14-2ea60fbfa590",
                            'Host': "94.130.238.184:8888",
                            'Accept-Encoding': "gzip, deflate",
                            'Content-Length': "2796",
                            'Connection': "keep-alive",
                            'cache-control': "no-cache"
                        }

def check_must_crwal(page):
    now = datetime.datetime.now()
    x = CrawlReport.objects.filter(page=page.id, status='pending')
    if x.count() == 0:
        crawl(page)
    else:
        last_report = x.last()
        if int((now - last_report.created_at).total_seconds()/(3600)) >= page.crawl_interval:
            last_report.status = 'failed'
            last_report.save()
            crawl(page)


@crawler.task(name='check_agencies')
def check():
    logger.info("---***> Check_agencies is started <***----")
    agencies = Agency.objects.filter(status= True).values_list('id', flat= True)
    pages = Page.objects.filter(agency__in=agencies)
    now = datetime.datetime.now()
    for page in pages:
        if page.last_crawl is None:
            check_must_crwal(page)
        else:
            diff_hour = int((now - page.last_crawl).total_seconds()/(3600))
            if diff_hour >= page.crawl_interval:
                check_must_crwal(page)



def crawl(page):
    logger.info("---> Page %s must be crawled", page.url)
    serializer = AgencyPageStructureSerializer(page)
    page_crawl.delay(serializer.data)


@crawler.task(name='page_crawl')
def page_crawl(page_structure):
    logger.info("---> Page crawling is started")
    CrawlerEngine(page_structure)


@crawler.task(name='page_crawl_repetitive')
def page_crawl_repetitive(page_structure):
    logger.info("---> Page crawling is started")
    CrawlerEngine(page_structure, repetitive= True)


@crawler.task(name='redis_exporter')
def redis_exporter():
    logger.info("---> Redis exporter is started")
    API_KEY = '1395437640:AAFZ1mkohxundOSBwBek1B8SPnApO4nIIMo'
    bot = telegram.Bot(token=API_KEY)
    pages = Page.objects.filter(status=True)

    for key in redis_news.scan_iter("*"):
        data = (redis_news.get(key).decode('utf-8'))
        try:
            data = json.loads(data)
            page = pages.filter(pk=data['page_id']).first()
            if page.iv_code is not None:
                data['iv_link'] = "https://t.me/iv?url={}&rhash={}".format(data['link'], page.iv_code)
            message = data['link']
            temp_code = """
{0}
            """
            temp_code = temp_code.format(page.message_code)
            try:
                temp_code = temp_code + '\n' + 'bot.send_message(chat_id=page.telegram_channel, text=message)'
                exec(temp_code)
                time.sleep(1)
            except Exception as e:
                logger.info("Getting attr %s got error", key)
                logger.info("The code was:\n %s ", temp_code)
                logger.info("Error was:\n %s", str(e))
        except Exception as e:
            print('ERRRORRRR  {}'.format(key))
            print(str(e))
        finally:
            redis_news.delete(key)

    for key in redis_news.scan_iter("*upwork*"):
        data = (redis_news.get(key).decode('utf-8'))
        try:
            data = json.loads(data)
            message = "https://t.me/iv?url={}&rhash=27e79aa0d36cae".format(data['link'])
            # message = "https://t.me/iv?url={}&rhash=27e79aa0d36cae\n\nLink: {}".format(data['link'], data['link'])
            bot.send_message(chat_id='@upwork_careers', text=message)
            time.sleep(0.5)
        except Exception as e:
            print('ERRRORRRR upwork')
            print(str(e))
        finally:
            redis_news.delete(key)


@crawler.task(name='fetch_alexa_rank')
def fetch_alexa_rank(agency_id, agency_url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Remote("http://crawler_chrome_browser:4444/wd/hub",
                                        desired_capabilities=DesiredCapabilities.CHROME,
                                        options=options)
    driver.header_overrides = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.11 (KHTML, like Gecko) '
        'Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    driver.get('https://www.alexa.com/siteinfo/{}'.format(agency_url))
    doc = BeautifulSoup(driver.page_source, 'html.parser')
    global_rank = doc.find('div', {'class': 'rankmini-rank'}).text. \
                                replace('#', '').replace('\t','').replace('\n', '').replace(',','')
    Agency.objects.filter(pk=agency_id).update(alexa_global_rank=global_rank)
