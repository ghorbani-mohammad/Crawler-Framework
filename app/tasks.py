from __future__ import absolute_import, unicode_literals
import requests
from bs4 import BeautifulSoup
import logging, datetime, redis, requests, json


from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from .celery import app
from celery import current_app
from agency.models import Agency, AgencyPageStructure, CrawlReport
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer
from agency.crawler_engine import CrawlerEngine


logger = logging.getLogger('django')

# TODO: configs must be dynamic
redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
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


@app.task(name='check_agencies')
def check():
    logger.info("---***> Check_agencies is started <***----")
    agencies = Agency.objects.filter(status= True).values_list('id', flat= True)
    pages = AgencyPageStructure.objects.filter(agency__in=agencies)
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


@app.task(name='page_crawl')
def page_crawl(page_structure):
    logger.info("---> Page crawling is started")
    CrawlerEngine(page_structure)


@app.task(name='redis_exporter')
def redis_exporter():
    logger.info("---> Redis exporter is started")
    # try:
    for key in redis_news.keys('*'):
        data = (redis_news.get(key).decode('utf-8'))
        try:
            data = json.loads(data)
        except:
            print(data)
            continue
        if not 'date' in data:
            data['date'] = int(datetime.datetime.now().timestamp())
        if not 'agency_id' in data:
            redis_news.delete(key)
            continue
        data['agency_id'] = int(data['agency_id'])
        try:
            response = requests.request("GET", Exporter_API_URI, data=json.dumps(data), headers=Exporter_API_headers)
        except Exception:
            print('get error')
        if response.status_code == 200 or response.status_code == 406:
            logging.error(response.status_code)
            redis_news.delete(key)
        elif response.status_code == 400:
            logging.error(response.status_code)
            redis_news.delete(key)
            logging.error('Exporter error. code: %s || message: %s', str(response.status_code), str(response.text))
            logging.error('Redis-key: %s', str(key))
        elif response.status_code == 500:
            logging.error('Exporter error. code: %s || message: %s', str(response.status_code), str(response.text))
            logging.error('Redis-key: %s', str(key))
            return
        else:
            logging.error('Exporter error. code: %s || message: %s', str(response.status_code), str(response.text))
            logging.error('Redis-key: %s', str(key))
    # except Exception:
    #     logging.error('Exporter error code: %s',str(Exception))


@app.task(name='fetch_alexa_rank')
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
