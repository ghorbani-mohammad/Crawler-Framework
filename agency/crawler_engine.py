"""
    Required modules for requests and bs4
"""
import logging, redis, json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger('django')
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')


class CrawlerEngine():
    """
    This class extract news links from a page and then go to them and extract their informations
    """
    def __init__(self, page, header=None):
        # TODO: ip and port of webdriver must be dynamic
        self.driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub",
                                        desired_capabilities=DesiredCapabilities.CHROME,
                                        options=options)
        # TODO: ip and port of redis must be dynamic
        self.redis_news = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.redis_duplicate_checker = redis.StrictRedis(host='localhost', port=6379, db=1)
        self.page = page
        self.header = header
        self.run()

    def fetch_links(self):
        links = []
        self.driver.get(self.page['url'])
        doc = BeautifulSoup(self.driver.page_source, 'html.parser')
        attribute = self.page['news_links_structure']
        # logger.info(attribute)
        tag = attribute['tag']
        del attribute['tag']
        code = ''
        if 'code' in attribute.keys():
            code = attribute['code']
            del attribute['code']
        elements = doc.findAll(tag, attribute)
        if code != '':
            temp_code = """
{0}
            """
            temp_code = temp_code.format(code)
            logger.info("Executing code")
            logger.info(temp_code)
            exec(temp_code)
            logger.info("executed code")
        else:
            for element in elements:
                links.append(element['href'])
        logger.info("Fetched links are:")
        logger.info(links)
        self.news_links = links
    
    # TODO: Maek crawl_news_page as task function
    def crawl_one_page(self, link):
        logger.info("Fetching news started for %s", link)
        meta = self.page['news_meta_structure']
        article = {}
        article['link'] = link
        self.driver.get(link)
        doc = BeautifulSoup(self.driver.page_source, 'html.parser')
        for key in meta.keys():
            attribute = meta[key].copy()
            # logger.info(attribute)
            tag = attribute['tag']
            del attribute['tag']
            code = ''
            if 'code' in attribute.keys():
                code = attribute['code']
                del attribute['code']
            element = doc.find(tag, attribute)
            if element is None:
                break
            if code != '':
                temp_code = """
{0}
                """
                temp_code = temp_code.format(code)
                exec(temp_code)
            article[key] = element.text
        logger.info(article)
        self.save_to_redis(article)


    def save_to_redis(self, article):
        # save to redis for 5 days
        # TODO: expiration must be dynamic
        self.redis_news.set(article['link'], json.dumps(article))
        self.redis_duplicate_checker.set(article['link'], "", ex=432000)
    
    def check_links(self):
        for link in self.news_links:
            if self.redis_duplicate_checker.exists(link):
                logger.info("duplicate")
                continue
            else:
                self.crawl_one_page(link)

    def run(self):
        logger.info("------> Fetching links from %s started", self.page['url'])
        self.fetch_links()
        logger.info("------> We found %s number of links: ", len(self.news_links))
        self.check_links()