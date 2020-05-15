"""
    Required modules for requests and bs4
"""
import logging, redis, json, time, datetime
from bs4 import BeautifulSoup
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from agency.models import Agency, AgencyPageStructure, CrawlReport

logger = logging.getLogger('django')

class CrawlerEngine():
    """
    This class extract news links from a page and then go to them and extract their informations
    """
    def __init__(self, page, header=None):
        # TODO: ip and port of webdriver must be dynamic
        
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--enable-automation"); 
        options.add_argument("--no-sandbox"); 
        self.driver = webdriver.Remote("http://localhost:4444/wd/hub",
                                        desired_capabilities=DesiredCapabilities.CHROME,
                                        options=options)
        self.driver.header_overrides = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.11 (KHTML, like Gecko) '
            'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        # TODO: ip and port of redis must be dynamic
        self.redis_news = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.redis_duplicate_checker = redis.StrictRedis(host='localhost', port=6379, db=1)
        self.page = page
        self.report = CrawlReport.objects.create(page_id=self.page['id'], status='pending')
        self.header = header
        self.run()

    def fetch_links(self):
        """ Extract links in a page. Links that have specified structure will be extracted.
        """        
        links = []
        self.driver.get(self.page['url'])
        # f = open('page_content.txt', 'w')
        # f.write(self.driver.page_source)
        # f.close()
        doc = BeautifulSoup(self.driver.page_source, 'html.parser')
        attribute = self.page['news_links_structure']
        # logger.info(type(attribute))
        attribute = json.dumps(attribute)
        attribute = json.loads(attribute)
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
        # logger.info("Fetched links are:")
        # logger.info(links)
        self.fetched_links = links
        self.fetched_links_count = len(links)
    
    # TODO: Maek crawl_news_page as task function
    def crawl_one_page(self, link):
        """Gets one page and crawl it
        
        Arguments:
            link {[string]} -- [link of page]
        """        
        meta = self.page['news_meta_structure']
        article = {}
        article['link'] = link
        self.driver.get(link)
        # TODO: sleep to page load must be dynamic
        time.sleep(4)
        doc = BeautifulSoup(self.driver.page_source, 'html.parser')
        for key in meta.keys():
            attribute = meta[key].copy()
            tag = attribute['tag']
            del attribute['tag']
            if tag == 'value':
                article[key] = attribute['value']
                continue
            if tag == 'code':
                code = attribute['code']
                temp_code = """
{0}
                """
                temp_code = temp_code.format(code)
                try:
                    exec(temp_code)
                except Exception as e:
                    logger.info("Getting attr %s got error", key)
                    logger.info("The code was:\n %s ", temp_code)
                    logger.info("Error was:\n %s", str(e))
                continue
            code = ''
            if 'code' in attribute.keys():
                code = attribute['code']
                del attribute['code']
            element = doc.find(tag, attribute)
            if element is None:
                logger.info("element is null")
                logger.info(attribute)
                break
            if code != '':
                temp_code = """
{0}
                """
                temp_code = temp_code.format(code)
                try:
                    exec(temp_code)
                except Exception as e:
                    logger.info("Getting attr %s got error", key)
                    logger.info("The code was:\n %s ", temp_code)
                    logger.info("Error was:\n %s", str(e))
            else:
                article[key] = element.text
        # article['source'] = str(self.page['agency'])
        logger.info(article)
        self.save_to_redis(article)


    def save_to_redis(self, article):
        """ Save fetched article(news) into redis
        
        Arguments:
            article {[aticle]} -- [a json of article attribute]
        """        
        # save to redis for 5 days
        # TODO: expiration must be dynamic
        self.redis_news.set(article['link'], json.dumps(article))
        self.redis_duplicate_checker.set(article['link'], "", ex=432000)
    
    def check_links(self):
        """ Cheking links in a page. If a link is not crawled before we will crawl it now
        """        
        counter = self.fetched_links_count
        for link in self.fetched_links:
            if self.redis_duplicate_checker.exists(link):
                # logger.info("duplicate")
                counter -= 1
                continue
            else:
                # logger.info("Fetching news started for %s", link)
                self.crawl_one_page(link)
        # TODO: page muse be valued in constructor
        page_structure = AgencyPageStructure.objects.get(id=self.page['id'])
        page_structure.last_crawl = datetime.datetime.now()
        page_structure.save()
        self.report.fetched_links = self.fetched_links_count
        self.report.new_links = counter
        self.report.status = 'complete'
        self.report.save()
        self.driver.quit()

    def run(self):
        logger.info("------> Fetching links from %s started", self.page['url'])
        self.fetch_links()
        logger.info("------> We found %s number of links: ", self.fetched_links_count)
        self.check_links()