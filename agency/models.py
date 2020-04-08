from django.db import models

# Create your models here.
class Agency(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    website = models.TextField(null=False)
    crawl_interval = models.IntegerField(default=12)
    status = models.BooleanField(default=1)
    last_crawl = models.DateTimeField()
    last_crawl_duration = models.TextField()
    last_crawl_status = models.BooleanField()
    number_of_crawls = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()