# Don't remove re package, this package used dynamically in code
import re, redis, json, time, traceback, validators
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.utils import timezone
from celery.utils.log import get_task_logger

from . import models, utils

logger = get_task_logger(__name__)


class CrawlerEngine:
    def __init__(self, page, repetitive=False, header=None):
        options = Options()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--enable-javascript")
        self.driver = webdriver.Remote(
            "http://crawler_chrome:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
        # set headers to looks like a common user
        self.driver.header_overrides = utils.DEFAULT_HEADER
        self.redis_news = redis.StrictRedis(host="crawler_redis", port=6379, db=0)
        self.redis_duplicate_checker = redis.StrictRedis(
            host="crawler_redis", port=6379, db=1
        )
        self.log_messages = ""
        self.page = models.Page.objects.get(id=page["id"])
        self.page.lock = True
        self.page.save()
        self.report = models.Report.objects.create(
            page_id=self.page.id, status="pending"
        )
        self.header = header
        self.repetitive = repetitive
        self.run()

    def register_log(self, description, e, page, url):
        models.Log.objects.create(
            page=page,
            description=description,
            url=url,
            phase=models.Log.CRAWLING,
            error=e,
        )

    def fetch_links(self):
        data = []
        self.driver.get(self.page.url)
        time.sleep(self.page.links_sleep)
        if self.page.take_picture:
            self.driver.get_screenshot_as_file(
                "static/crawler/static/{}.png".format(self.report.id)
            )
            self.report.picture = "static/crawler/static/{}.png".format(self.report.id)
            self.report.save()
        doc = BeautifulSoup(self.driver.page_source, "html.parser")
        attribute = self.page.structure.news_links_structure
        tag = attribute["tag"]
        del attribute["tag"]
        if "code" in attribute.keys():
            del attribute["code"]
        elements = doc.findAll(tag, attribute)
        if self.page.structure.news_links_code != "":
            exec(self.page.structure.news_links_code)
        else:
            for element in elements:
                data.append(element["href"])
        logger.info(f"Fetched data are: {data}")
        self.fetched_links = data
        self.fetched_links_count = len(data)
        self.report.fetched_links = self.fetched_links_count
        self.report.save()

    # TODO: Make crawl_news_page as task function
    def crawl_one_page(self, data, fetch_contet):
        meta = self.page.structure.news_meta_structure
        article = data
        article["page_id"] = self.page.id
        if fetch_contet:
            self.driver.get(data["link"])
            time.sleep(self.page.load_sleep)
            doc = BeautifulSoup(self.driver.page_source, "html.parser")
            if meta is not None:
                for key in meta.keys():
                    attribute = meta[key].copy()
                    tag = attribute["tag"]
                    del attribute["tag"]
                    if tag == "value":
                        article[key] = attribute["value"]
                        continue
                    if tag == "code":
                        code = attribute["code"]
                        temp_code = """
{0}
                        """
                        temp_code = temp_code.format(code)
                        try:
                            exec(temp_code)
                        except Exception as e:
                            logger.error(traceback.format_exc())
                            desc = "tag code, executing code made error, the code was {}".format(
                                temp_code
                            )
                            self.register_log(desc, e, self.page, data["link"])
                        continue
                    code = ""
                    if "code" in attribute.keys():
                        code = attribute["code"]
                        del attribute["code"]
                    element = doc.find(tag, attribute)
                    if element is None:
                        desc = f"tag was: {tag} *** and attribute was {attribute}"
                        error = "element is null"
                        self.register_log(desc, error, self.page, data["link"])
                        break
                    if code != "":
                        temp_code = """
{0}
                        """
                        temp_code = temp_code.format(code)
                        try:
                            exec(temp_code)
                        except Exception as e:
                            logger.error(traceback.format_exc())
                            desc = f"tag code, executing code made error, the code was {temp_code}"
                            self.register_log(desc, e, self.page, data["link"])
                    else:
                        article[key] = element.text
        logger.info(f"crawl_one_page: {article}")
        self.save_to_redis(article)

    def save_to_redis(self, article):
        self.redis_news.set(article["link"], json.dumps(article))
        self.redis_duplicate_checker.set(
            article["link"], "", ex=self.page.days_to_keep * 60 * 60 * 24
        )

    def check_data(self):
        counter = self.fetched_links_count
        for data in self.fetched_links:
            if not self.repetitive and self.redis_duplicate_checker.exists(
                data["link"]
            ):
                counter -= 1
                continue
            else:
                self.crawl_one_page(data, self.page.fetch_content)
        self.page.last_crawl = timezone.localtime()
        self.page.last_crawl_count = self.fetched_links_count
        self.page.lock = False
        self.page.save()
        self.report.new_links = counter
        self.report.status = "complete"
        self.report.log = self.log_messages
        self.report.save()
        self.driver.quit()

    def custom_logging(self, message):
        logger.info(message)
        self.log_messages += "{} \n".format(message)

    def run(self):
        logger.info(f"---> Fetching links from {self.page} started")
        self.fetch_links()
        logger.info(
            f"---> We found {self.fetched_links_count} number of links for {self.page}"
        )
        self.check_data()


# Crawler version 2
class CrawlerEngineV2:
    def __init__(self, header=None):
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--enable-automation")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Remote(
            "http://crawler_chrome_browser:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
        self.driver.header_overrides = utils.DEFAULT_HEADER

    def get_links(self, structure, url):
        links = []
        self.driver.get(url)
        doc = BeautifulSoup(self.driver.page_source, "html.parser")
        attribute = json.dumps(structure)
        attribute = json.loads(attribute)
        tag = attribute["tag"]
        del attribute["tag"]
        code = ""
        if "code" in attribute.keys():
            code = attribute["code"]
            del attribute["code"]
        elements = doc.findAll(tag, attribute)
        if code != "":
            temp_code = """
{0}
            """
            temp_code = temp_code.format(code)
            exec(temp_code)
        else:
            for element in elements:
                links.append(element["href"])
        links = set([link for link in links if validators.url(link)])
        return links

    def get_content(self, structure, url):
        article = {}
        article["link"] = url
        self.driver.get(url)
        # TODO: sleep to page load must be dynamic
        doc = BeautifulSoup(self.driver.page_source, "html.parser")
        for key in structure.keys():
            attribute = structure[key].copy()
            tag = attribute["tag"]

            del attribute["tag"]
            if tag == "value":
                article[key] = attribute["value"]
                print(
                    "\tspecified tag get's value directly and it's value is: \n {}".format(
                        attribute["value"]
                    )
                )
                continue
            if tag == "code":
                code = attribute["code"]
                temp_code = """
{0}
                """
                temp_code = temp_code.format(code)
                try:
                    exec(temp_code)
                except Exception as e:
                    print("Getting attr {} got error".format(key))
                    print("The code was:\n {} ".format(temp_code))
                    print("Error was:\n {}".format(str(e)))
                continue
            code = ""
            if "code" in attribute.keys():
                code = attribute["code"]
                del attribute["code"]
            print("key: {} tag: {} attr: {}".format(key, tag, attribute))
            element = doc.find(tag, attribute)
            if element is None:
                print("element is null, attribute: {}".format(attribute))
                break
            if code != "":
                temp_code = """
{0}
                """
                temp_code = temp_code.format(code)
                try:
                    exec(temp_code)
                except Exception as e:
                    print("Getting attr {} got error".format(key))
                    print("The code was:\n {} ".format(temp_code))
                    print("Error was:\n {}".format(str(e)))
            else:
                article[key] = element.text
        return article
