from django.db import models
# from django.contrib.postgres.fields import JSONField
import jsonfield


# Create your models here.
class Agency(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    website = models.CharField(max_length=100, null=False)
    crawl_headers = jsonfield.JSONField(null=True, blank=True, default={})
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

class AgencyPageStructure(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING)
    page = models.CharField(max_length=300, null=False)
    crawl_interval = models.IntegerField(default=12)
    news_links_structure = jsonfield.JSONField()
    news_meta_structure = jsonfield.JSONField()