from django.db import models
from django.contrib.postgres.fields import JSONField


class Agency(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    country = models.CharField(max_length=20, default='NA')
    website = models.CharField(max_length=100, null=False)
    crawl_headers = JSONField(null=True, blank=True, default=dict)
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CrawlReport(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING)
    last_crawl = models.DateTimeField(null=True)
    last_crawl_duration = models.DateTimeField(null=True)
    last_crawl_status = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AgencyPageStructure(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING)
    url = models.CharField(max_length=300, null=False)
    crawl_interval = models.IntegerField(default=12)
    last_crawl = models.DateTimeField(null=True, editable=False)
    news_links_structure = JSONField()
    news_meta_structure = JSONField()
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
    