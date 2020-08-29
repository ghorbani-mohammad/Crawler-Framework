from django.db import models
from django.contrib.postgres.fields import JSONField


class Agency(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    country = models.CharField(max_length=20, default='NA')
    website = models.CharField(max_length=100, null=False, unique=True)
    alexa_global_rank = models.IntegerField(default=0, null=True)
    crawl_headers = JSONField(null=True, blank=True, default=dict)
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class PageStructure(models.Model):
    name = models.CharField(max_length=20, null=True)
    news_links_structure = JSONField()
    news_meta_structure = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name is not None else 'None'


class Page(models.Model):
    agency = models.ForeignKey(Agency, related_name='pages', on_delete=models.CASCADE)
    url = models.CharField(max_length=1000, null=False, unique=True)
    crawl_interval = models.IntegerField(default=2)
    load_sleep = models.IntegerField(default=4)
    last_crawl = models.DateTimeField(null=True)
    status = models.BooleanField(default=1)
    fetch_content = models.BooleanField(default=1)
    structure = models.ForeignKey(PageStructure, on_delete=models.SET_NULL, null=True, blank=True)
    telegram_channel = models.CharField(max_length=100, null=True, blank=True)
    iv_code = models.CharField(max_length=100, null=True, blank=True)
    message_code = models.TextField(default=None, null=True, blank=True)
    take_picture = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url


class CrawlReport(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='report')
    status = models.CharField(max_length=300, null=True)
    fetched_links = models.IntegerField(default=0)
    new_links = models.IntegerField(default=0)
    picture = models.ImageField(upload_to='.static/crawler/static', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.page.url
