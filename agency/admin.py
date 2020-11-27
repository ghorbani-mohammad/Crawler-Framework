from prettyjson import PrettyJSONWidget
from django.contrib.postgres import fields
from djangoeditorwidgets.widgets import MonacoEditorWidget
from django_json_widget.widgets import JSONEditorWidget
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.contrib import messages
from django.utils.translation import ngettext

from agency.models import Agency, Page, Report, Structure, Log
from agency.serializer import AgencyPageStructureSerializer
from reusable import jalali


@admin.register(Report)
class CrawlAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'url', 'fetched_links', 'new_links', 'started_at', 'duration', 'status', 'image_tag')
    list_per_page = 30
    list_filter = ['page__agency']
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
            "news_links_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            )
        }


@admin.register(Structure)
class PageStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget(height="320px", width="40%")},
    }
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
    list_display = ('agency', 'page_url', 'crawl_interval', 'last_crawl', 'status', 'fetch_content', 'take_picture')
    list_editable = ('crawl_interval',)
    list_filter = ['agency']
    fields = (
        'agency', 'url', 'structure',
        ('crawl_interval', 'load_sleep', 'links_sleep'),
        ('status', 'fetch_content', 'take_picture'),
        ('telegram_channel', 'iv_code'),
        'message_code',
        'last_crawl', 
    )


    def page_url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.url)

    readonly_fields = ("last_crawl",)
    actions = [crawl_action, crawl_action_ignore_repetitive]

    def agency(self, obj):
        return obj.page.agency.name

    form = PageAdminForm


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('agency', 'base', 'source', 'error', 'short_description', 'created_at', 'phase')
    list_filter = ['page__agency', 'phase']
    
    def source(self, obj):
        if obj.page is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.page.url)
        return ''
    
    def base(self, obj):
        if obj.url is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.url)
        return ''
    
    def agency(self, obj):
        if obj.page is not None:
            return obj.page.agency.name
        return ''
    
    def short_description(self, obj):
        from django.template.defaultfilters import truncatechars  # or truncatewords
        return truncatechars(obj.description, 100)
    
    def has_change_permission(self, request, obj=None):
        return False
