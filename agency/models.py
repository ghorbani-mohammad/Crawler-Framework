from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Agency(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    website = models.TextField(null=False)
    crawl_interval = models.IntegerField(default=12)
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CrawlReport(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING)
    last_crawl = models.DateTimeField(null=True)
    last_crawl_duration = models.DateTimeField(null=True)
    last_crawl_status = models.BooleanField(null=True)

class AgencyPageStructure(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING)
    page = models.TextField(null=False)
    structure = JSONField()