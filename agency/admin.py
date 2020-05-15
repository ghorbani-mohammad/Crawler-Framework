import datetime as dt
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django import forms
from agency.models import Agency, AgencyPageStructure, CrawlReport


@admin.register(CrawlReport)
class CrawlAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'page', 'fetched_links', 'new_links', 'started_at', 'duration', 'status')
    list_per_page = 10

    def agency(self, obj):
        return obj.page.agency.name

    def started_at(self, obj):
        return obj.created_at

    def duration(self, obj):
        x = round((obj.updated_at - obj.created_at).total_seconds())
        return "{} sec".format(x)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'website', 'status', 'alexa_global_rank')


class AgencyPageStructureForm(forms.ModelForm):

    class Meta:
        model = AgencyPageStructure
        fields = '__all__'
        widgets = {
            'news_links_structure': PrettyJSONWidget(),
            'news_meta_structure': PrettyJSONWidget(),
        }


@admin.register(AgencyPageStructure)
class AgencyPageStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'url', 'crawl_interval', 'last_crawl', 'status')

    form = AgencyPageStructureForm

    def agency(self, obj):
        return obj.page.agency.name
