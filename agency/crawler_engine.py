import logging, redis, json, time, datetime, time
from bs4 import BeautifulSoup
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from agency.models import Page, Report

logger = logging.getLogger('django')

class CrawlerEngine():
    def __init__(self, page, repetitive= False, header=None):
        # TODO: ip and port of webdriver must be dynamic
        
        options = Options()
        # options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--enable-javascript")
        # options.add_argument("--enable-automation"); 
        # options.add_argument("--no-sandbox"); 
        self.driver = webdriver.Remote("http://crawler_chrome_browser:4444/wd/hub",
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
        self.redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
        self.redis_duplicate_checker = redis.StrictRedis(host='crawler_redis', port=6379, db=1)
        self.page = Page.objects.get(id=page['id'])
        self.report = Report.objects.create(page_id=self.page.id, status='pending')
        self.header = header
        self.repetitive = repetitive
        self.run()

    def fetch_links(self):
        links = []
        self.driver.get(self.page.url)
        time.sleep(self.page.links_sleep)
        # f = open('page_content_{}.html'.format(str(datetime.datetime.now())), 'w')
        # f.write(self.driver.page_source)
        # f.close()
        if self.page.take_picture:
            self.driver.get_screenshot_as_file('static/crawler/static/{}.png'.format(self.report.id))
            self.report.picture = 'static/crawler/static/{}.png'.format(self.report.id)
            self.report.save()
        doc = BeautifulSoup(self.driver.page_source, 'html.parser')
        attribute = self.page.structure.news_links_structure
        logger.info(type(attribute))
        attribute = json.dumps(attribute)
        attribute = json.loads(attribute)
        logger.info(attribute)
        tag = attribute['tag']
        del attribute['tag']
        if 'code' in attribute.keys():
            del attribute['code']
        print('specified tag for links')
        print(tag)
        print('specified attributes for links')
        print(attribute)
        elements = doc.findAll(tag, attribute)
        if self.page.structure.news_links_code != '':
            logger.info("Executing code")
            logger.info(self.page.structure.news_links_code)
            exec(self.page.structure.news_links_code)
            logger.info("executed code")
        else:
            for element in elements:
                links.append(element['href'])
        logger.info("Fetched links are:")
        logger.info(links)
        self.fetched_links = links
        self.fetched_links_count = len(links)
    
    # TODO: Make crawl_news_page as task function
    def crawl_one_page(self, link, fetch_contet):      
        meta = self.page.structure.news_meta_structure
        article = {}
        article['link'] = link
        article['page_id'] = self.page.id
        if fetch_contet:
            self.driver.get(link)
            # TODO: sleep to page load must be dynamic
            time.sleep(self.page.load_sleep)
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
        # save to redis for 5 days
        # TODO: expiration must be dynamic
        self.redis_news.set(article['link'], json.dumps(article))
        self.redis_duplicate_checker.set(article['link'], "", ex=432000)
    
    def check_links(self):
        """ Cheking links in a page. If a link is not crawled before we will crawl it now
        """        
        page = Page.objects.get(id=self.page.id)
        counter = self.fetched_links_count
        for link in self.fetched_links:
            if not self.repetitive and self.redis_duplicate_checker.exists(link):
                # logger.info("duplicate")
                counter -= 1
                continue
            else:
                # logger.info("Fetching news started for %s", link)
                self.crawl_one_page(link, page.fetch_content)
        # TODO: page muse be valued in constructor
        page.last_crawl = datetime.datetime.now()
        page.save()
        self.report.fetched_links = self.fetched_links_count
        self.report.new_links = counter
        self.report.status = 'complete'
        self.report.save()
        self.driver.quit()

    def run(self):
        logger.info("------> Fetching links from %s started", self.page.url)
        self.fetch_links()
        logger.info("------> We found %s number of links: ", self.fetched_links_count)
        self.check_links()