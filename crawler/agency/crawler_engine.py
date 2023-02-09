# Don't remove re package, this package used dynamically in code
import re
import json
import time
import redis
import traceback
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException

from django.conf import settings
from django.utils import timezone
from celery.utils.log import get_task_logger

from . import models, utils

logger = get_task_logger(__name__)
redis_news = redis.StrictRedis(host="crawler_redis", port=6379, db=0)
redis_duplicate_checker = redis.StrictRedis(host="crawler_redis", port=6379, db=1)


class CrawlerEngine:
    def __init__(self, page, repetitive=False, header=None):
        """Initialize engine for getting data from a page

        Args:
            page (page): Page object
            repetitive (bool, optional): If true we will get data from the repetitive links in the page. Defaults to False.
            header (json, optional): Custom header. Defaults to None.
        """
        try:
            caps = DesiredCapabilities().FIREFOX
            caps["pageLoadStrategy"] = "eager"  # interactive
            self.driver = webdriver.Remote(
                "http://crawler_selenium_hub:4444",
                desired_capabilities=caps,
                options=utils.get_browser_options(),
            )
        except SessionNotCreatedException as e:
            error = f"{e}\n\n\n{traceback.format_exc()}"
            logger.info(error)
            return
        self.driver.set_page_load_timeout(5)
        self.driver.header_overrides = utils.DEFAULT_HEADER
        self.log_messages = ""
        self.header = header
        self.repetitive = repetitive
        self.fetched_links = []
        self.fetched_links_count = 0
        self.page = models.Page.objects.get(id=page["id"])
        self.page.lock = True
        self.page.save()
        self.report = models.Report.objects.create(
            page_id=self.page.id, status=models.Report.PENDING
        )
        self.custom_logging(
            f"Crawl **started** for page: {self.page} with repetitive: {self.repetitive}"
        )
        self.run()
        self.custom_logging(
            f"Crawl **finished** for page: {self.page} with repetitive: {self.repetitive}"
        )

    def register_log(self, description, e, page, url):
        """Custom registering logs. Logs are stored into the db.

        Args:
            description (str): extra description of the error
            e (str): exception
            page (page): which page we have encountered error
            url (url): link of page
        """
        logger.error(traceback.format_exc())
        models.Log.objects.create(
            page=page,
            description=description,
            url=url,
            phase=models.Log.CRAWLING,
            error=e,
        )

    def fetch_links(self):
        """Fetch links from a page
        this function get links based on the specified structure from a page
        """
        data = []
        try:
            self.driver.get(self.page.url)
        except TimeoutException as e:
            warning = f"{e}\n\n\n{traceback.format_exc()}"
            logger.warning(warning)
            return
        except Exception as e:
            error = f"{e}\n\n\n{traceback.format_exc()}"
            logger.error(error)
            return
        time.sleep(self.page.links_sleep)
        if self.page.take_picture:
            # in debug mode static_root is none
            file_path = f"{settings.STATIC_ROOT or './static'}/{self.report.id}.png"
            self.driver.get_screenshot_as_file(file_path)
            self.report.picture = file_path
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
        self.custom_logging(f"Fetched data are: {data}")
        self.fetched_links = data
        self.fetched_links_count = len(data)
        self.report.fetched_links = self.fetched_links_count
        self.report.save()

    def crawl_one_page(self, data, fetch_content):
        """Get data from crawled link based on defined structure

        Args:
            data (json): data where we have link
            fetch_content (bool): wether we should open the link or not
        """
        meta = self.page.structure.news_meta_structure
        article = data
        article["page_id"] = self.page.id
        if fetch_content:
            try:
                self.driver.get(data["link"])
            except TimeoutException as e:
                logger.error(
                    f"error: {e}\nlink: {data['link']}\ntraceback: {traceback.format_exc()}"
                )
                return
            except Exception as e:
                logger.error(f"error: {e}\ntraceback: {traceback.format_exc()}")
                return
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
                        temp_code = utils.CODE.format(code)
                        try:
                            exec(temp_code)
                        except Exception as e:
                            desc = f"tag code, executing code made error, the code was {temp_code}"
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
                        temp_code = utils.CODE.format(code)
                        try:
                            exec(temp_code)
                        except Exception as e:
                            desc = f"tag code, executing code made error, the code was {temp_code}"
                            self.register_log(desc, e, self.page, data["link"])
                    else:
                        article[key] = element.text
        self.custom_logging(f"crawl_one_page: {article}")
        self.save_to_redis(article)

    def save_to_redis(self, article):
        """We store each link information as a json into Redis
        We also store link into duplicate checker for avoiding duplicate links

        Args:
            article (json): information about link
        """
        redis_news.set(f'links_{article["link"]}', json.dumps(article))
        redis_duplicate_checker.set(
            article["link"], "", ex=self.page.days_to_keep * 60 * 60 * 24
        )

    def check_data(self):
        """Here we check each link that we crawled in the fetch-links function.
        We call crawl-one-page on each link
        We count not duplicate links
        """
        counter = self.fetched_links_count
        for data in self.fetched_links:
            if not self.repetitive and redis_duplicate_checker.exists(data["link"]):
                counter -= 1
                continue
            else:
                self.crawl_one_page(data, self.page.fetch_content)
        self.page.last_crawl = timezone.localtime()
        self.page.last_crawl_count = self.fetched_links_count
        self.page.lock = False
        self.page.save()
        self.report.new_links = counter
        self.report.status = models.Report.COMPLETED
        self.report.log = self.log_messages
        self.report.save()

    def custom_logging(self, message):
        logger.info(message)
        self.log_messages += f"{message} \n"

    def run(self):
        """Run the crawler engine
        first: we get links from the specified page
        second: we get data from each page
        """
        self.custom_logging(f"---> Fetching links from {self.page} started")
        self.fetch_links()
        self.custom_logging(
            f"---> We found {self.fetched_links_count} number of links for {self.page}"
        )
        self.check_data()
        self.driver.quit()
