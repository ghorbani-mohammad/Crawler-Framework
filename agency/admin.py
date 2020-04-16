from django.contrib import admin

# Register your models here.
from agency.models import Agency, AgencyPageStructure, CrawlReport

admin.site.register(Agency)
admin.site.register(AgencyPageStructure)
# admin.site.register(CrawlReport)
