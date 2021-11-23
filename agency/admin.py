from rangefilter.filter import DateTimeRangeFilter

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.contrib.postgres import fields
from django.utils.translation import ngettext
from django_json_widget.widgets import JSONEditorWidget
from djangoeditorwidgets.widgets import MonacoEditorWidget

from agency.models import Agency
from agency.models import Agency, Page, Report, Structure, Log
from agency.serializer import AgencyPageStructureSerializer


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "agency",
        "url",
        "fetched_links",
        "new_links",
        "started_at",
        "duration",
        "image_tag",
    )
    list_per_page = 30
    list_filter = ["status", "page__agency", ("created_at", DateTimeRangeFilter)]
    search_fields = ["page__url"]

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
            return format_html(
                "<a href='{}'>Link</a>".format(
                    "https://www.mo-ghorbani.ir/static/"
                    + obj.picture.path.split("/")[-1]
                )
            )
        return ""

    image_tag.short_description = "Image"


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "country",
        "website",
        "status",
        "alexa_global_rank",
        "link_keep_days",
    )


class PageStructureForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"

        widgets = {
            "news_links_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            )
        }


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget(height="320px", width="40%")},
    }
    form = PageStructureForm


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {
            "message_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            )
        }


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (
        "agency",
        "page_url",
        "crawl_interval",
        "last_crawl2",
        "last_crawl_count",
        "status",
        "lock",
        "fetch_content",
        "take_picture",
    )
    list_editable = ("crawl_interval", "status")
    list_filter = ["status", "lock", "agency"]
    readonly_fields = ("last_crawl",)
    fields = (
        "agency",
        "url",
        "structure",
        ("crawl_interval", "load_sleep", "links_sleep"),
        ("status", "fetch_content", "take_picture", "lock"),
        ("telegram_channel", "iv_code"),
        "message_code",
        "last_crawl",
    )

    def page_url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.url)

    def last_crawl2(self, obj):
        if obj.last_crawl is not None:
            return obj.last_crawl.strftime("%h. %d %H:%M %p")

    # actions
    def crawl_action(modeladmin, request, queryset):
        from app.tasks import page_crawl

        for page in queryset:
            page_crawl.delay(AgencyPageStructureSerializer(page).data)
        modeladmin.message_user(
            request,
            ngettext(
                "%d page is in queue to crawl.",
                "%d pages are in queue to crawl.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )

    crawl_action.short_description = "Crawl page"

    def crawl_action_ignore_repetitive(modeladmin, request, queryset):
        from app.tasks import page_crawl_repetitive

        for page in queryset:
            page_crawl_repetitive.delay(AgencyPageStructureSerializer(page).data)
        modeladmin.message_user(
            request,
            ngettext(
                "%d page is in queue to crawl.",
                "%d pages are in queue to crawl.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )

    crawl_action_ignore_repetitive.short_description = "Crawl page with repetitive"

    actions = [crawl_action, crawl_action_ignore_repetitive]
    form = PageAdminForm


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        "agency",
        "base",
        "source",
        "error",
        "short_description",
        "created",
        "phase",
    )
    list_filter = ["page__agency", "phase"]

    def source(self, obj):
        if obj.page is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.page.url)
        return ""

    def created(self, obj):
        return obj.created_at.strftime("%h. %d %H:%M %p")

    def base(self, obj):
        if obj.url is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.url)
        return ""

    def agency(self, obj):
        if obj.page is not None:
            return obj.page.agency.name
        return ""

    def short_description(self, obj):
        from django.template.defaultfilters import truncatechars  # or truncatewords

        return truncatechars(obj.description, 50)

    def has_change_permission(self, request, obj=None):
        return False

    def url2(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}<a>", url=obj.url)
