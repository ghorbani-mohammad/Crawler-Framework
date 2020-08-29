import datetime as dt
from prettyjson import PrettyJSONWidget
from djangoeditorwidgets.widgets import MonacoEditorWidget
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.contrib import messages
from django.utils.translation import ngettext

from agency.models import Agency, Page, CrawlReport, PageStructure
from agency.serializer import AgencyPageStructureSerializer


@admin.register(CrawlReport)
class CrawlAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'url', 'fetched_links', 'new_links', 'started_at', 'duration', 'status', 'image_tag')
    list_per_page = 30
    search_fields = ['page__url']

    def url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.page.url)

    def agency(self, obj):
        return obj.page.agency.name

    def started_at(self, obj):
        return obj.created_at
    
    def duration(self, obj):
        x = round((obj.updated_at - obj.created_at).total_seconds())
        return "{} sec".format(x)

    def image_tag(self, obj):
        if obj.picture:
            return format_html("<a href='{}'>Link</a>".format('https://www.mo-ghorbani.ir/static/'+obj.picture.path.split('/')[-1]))
        return ""

    image_tag.short_description = 'Image'


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'website', 'status', 'alexa_global_rank')


class PageStructureForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'

        widgets = {
            'news_links_structure': PrettyJSONWidget(),
            'news_meta_structure': PrettyJSONWidget(),
            "news_links_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            )
        }


@admin.register(PageStructure)
class PageStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    form = PageStructureForm


def crawl_action(AgencyPageStructureAdmin, request, queryset):
    from app.tasks import page_crawl
    for page in queryset:
        page_crawl.delay(AgencyPageStructureSerializer(page).data)
    crawl_action.short_description = "Crawl page"
    AgencyPageStructureAdmin.message_user(request, ngettext(
        '%d page is in queue to crawl.',
        '%d pages are in queue to crawl.',
        len(queryset),
    ) % len(queryset), messages.SUCCESS)


def crawl_action_ignore_repetitive(AgencyPageStructureAdmin, request, queryset):
    from app.tasks import page_crawl_repetitive
    for page in queryset:
        page_crawl_repetitive.delay(AgencyPageStructureSerializer(page).data)
    crawl_action_ignore_repetitive.short_description = "Crawl page with repetitive"
    AgencyPageStructureAdmin.message_user(request, ngettext(
        '%d page is in queue to crawl.',
        '%d pages are in queue to crawl.',
        len(queryset),
    ) % len(queryset), messages.SUCCESS)


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'

        widgets = {
            "message_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            )
        }

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'page_url', 'crawl_interval', 'last_crawl', 'status', 'fetch_content', 'take_picture')

    def page_url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.url)

    readonly_fields = ("last_crawl",)
    actions = [crawl_action, crawl_action_ignore_repetitive]

    def agency(self, obj):
        return obj.page.agency.name

    form = PageAdminForm
