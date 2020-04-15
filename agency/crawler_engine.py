"""
    Required modules for requests and bs4
"""
import logging
import redis
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
            self.driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", 
                                            desired_capabilities=DesiredCapabilities.CHROME, 
                                            options=options)
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
        # logger.info(elements)
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
    
    def crawl_news_page(self):
        meta = self.page['news_meta_structure']
        logger.info(meta)
        logger.info(meta.keys())
        for link in self.news_links:
            logger.info("Crawl news: "+link)
            self.driver.get(link)
            doc = BeautifulSoup(self.driver.page_source, 'html.parser')
            logger.info(meta.keys())
            for key in meta.keys():
                attribute = meta[key].copy()
                logger.info(attribute)
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
                    logger.info(element.text)
                else:
                    logger.info(element.text)



    def run(self):
        logger.info(self.page['url'])
        logger.info("------> Fetching links started")
        self.fetch_links()
        logger.info("------> We found %s number of links: ", len(self.news_links))
        # self.crawl_news_page()