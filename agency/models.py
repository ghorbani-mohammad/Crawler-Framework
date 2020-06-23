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
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class AgencyPageStructure(models.Model):
    agency = models.ForeignKey(Agency, related_name='pages', on_delete=models.CASCADE)
    url = models.CharField(max_length=300, null=False, unique=True)
    crawl_interval = models.IntegerField(default=12)
    last_crawl = models.DateTimeField(null=True, editable=False)
    news_links_structure = JSONField()
    news_meta_structure = JSONField()
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url


class CrawlReport(models.Model):
    page = models.ForeignKey(AgencyPageStructure, on_delete=models.CASCADE, related_name='report')
    status = models.CharField(max_length=300, null=True)
    fetched_links = models.IntegerField(default=0)
    new_links = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    log = models.TextField(blank=True)

    def __str(self):
        return self.page.url


class Option(models.Model):
    key = models.CharField(max_length=70)
    value = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
