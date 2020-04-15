from __future__ import absolute_import, unicode_literals
import logging, datetime
from .celery import app
from agency.models import Agency, AgencyPageStructure
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer
from agency.crawler_engine import CrawlerEngine

logger = logging.getLogger('django')


@app.task(name='check_agencies')
def check():
    agencies = Agency.objects.filter(status= True).values_list('id', flat= True)
    pages = AgencyPageStructure.objects.filter(agency__in=agencies)
    now = datetime.datetime.now()
    for page in pages:
        if page.last_crawl is None:
            serializer = AgencyPageStructureSerializer(page)
            page_crawl.delay(serializer.data)
        else:
            logger.info(page.last_crawl)

@app.task(name='page_crawl')
def page_crawl(page_structure):
    logger.info("page crawling is started")
    x = CrawlerEngine(page_structure)
