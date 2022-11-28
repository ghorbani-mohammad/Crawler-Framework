from prettyjson import PrettyJSONWidget
from rangefilter.filter import DateTimeRangeFilter

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import ngettext
from django.template.defaultfilters import truncatechars
from djangoeditorwidgets.widgets import MonacoEditorWidget

from agency.serializer import PageSerializer
from reusable.admins import ReadOnlyAdminDateFields
from agency.models import Agency, Page, Report, Structure, Log, DBLogEntry


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_per_page = 30
    search_fields = ("page__url",)
    list_display = (
        "id",
        "page_name",
        "url",
        "status",
        "agency",
        "duration",
        "new_links",
        "image_tag",
        "started_at",
        "fetched_links",
    )
    readonly_fields = (
        "log",
        "page",
        "status",
        "picture",
        "new_links",
        "fetched_links",
    )
    list_filter = [
        "status",
        "page__agency",
        ("created_at", DateTimeRangeFilter),
    ]

    def url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.page.url)

    def agency(self, obj):
        return obj.page.agency.name

    def started_at(self, obj):
        return obj.created_at

    def duration(self, obj):
        elapsed_seconds = round((obj.updated_at - obj.created_at).total_seconds())
        return f"{elapsed_seconds} sec"

    def image_tag(self, obj):
        if obj.picture:
            url = "https://www.mo-ghorbani.ir/static/" + obj.picture.path.split("/")[-1]
            return format_html(f"<a href='{url}'>Link</a>")

    image_tag.short_description = "Image"


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_filter = ("status",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_display = (
        "id",
        "name",
        "country",
        "website",
        "status",
        "link_keep_days",
        "pages_count",
        "created_at",
    )


class StructureForm(forms.ModelForm):
    class Meta:
        model = Structure
        fields = "__all__"
        widgets = {
            "news_meta_structure": PrettyJSONWidget(),
            "news_links_structure": PrettyJSONWidget(),
            "news_links_code": MonacoEditorWidget(
                attrs={"data-wordwrap": "on", "data-language": "python"}
            ),
        }


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
        "updated_at",
    )
    form = StructureForm


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
    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        return qs.filter(agency__status=True)

    def get_ordering(self, request):
        return ["-last_crawl"]

    form = PageAdminForm
    list_filter = (
        "lock",
        "status",
        "agency",
    )
    list_editable = (
        "status",
        "crawl_interval",
    )
    readonly_fields = ("last_crawl",) + ReadOnlyAdminDateFields.readonly_fields
    list_display = (
        "get_masked_name",
        "agency",
        "page_url",
        "crawl_interval",
        "get_last_crawl",
        "get_last_crawl_count",
        "status",
        "today_crawl_count",
        "lock",
        "fetch_content",
        "take_picture",
    )
    fields = (
        "name",
        "agency",
        "url",
        "structure",
        ("crawl_interval", "load_sleep", "links_sleep"),
        ("status", "fetch_content", "take_picture", "lock"),
        ("telegram_channel", "iv_code"),
        "message_code",
        "last_crawl",
        ("created_at", "updated_at", "deleted_at"),
    )

    def page_url(self, obj):
        return format_html("<a href='{url}'>Link</a>", url=obj.url)

    @admin.display(description="NAME")
    def get_masked_name(self, instance):
        return instance.masked_name

    @admin.display(description="L. Crawl")
    def get_last_crawl(self, instance):
        return instance.get_last_crawl_at

    @admin.display(description="L. Count")
    def get_last_crawl_count(self, instance):
        if instance.last_crawl_count:
            return instance.last_crawl_count

    # actions
    def crawl_action(modeladmin, request, queryset):
        from agency.tasks import page_crawl

        for page in queryset:
            page_crawl.delay(PageSerializer(page).data)
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
        from agency.tasks import page_crawl_repetitive

        for page in queryset:
            page_crawl_repetitive.delay(PageSerializer(page).data)
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
    actions = (
        crawl_action,
        crawl_action_ignore_repetitive,
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "base",
        "phase",
        "error",
        "agency",
        "source",
        "created_at",
        "short_description",
    )
    list_filter = ("phase", "page__agency")

    def source(self, obj):
        if obj.page is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.page.url)

    def created_at(self, obj):
        return obj.created_at.strftime("%h. %d %H:%M %p")

    def base(self, obj):
        if obj.url is not None:
            return format_html("<a href='{url}'>Link</a>", url=obj.url)

    def agency(self, obj):
        if obj.page is not None:
            return obj.page.agency.name

    def short_description(self, obj):
        return truncatechars(obj.description, 50)

    def has_change_permission(self, request, obj=None):
        return False

    def url2(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}<a>", url=obj.url)


@admin.register(DBLogEntry)
class DBLogEntryAdmin(admin.ModelAdmin):
    list_filter = ("level",)
    readonly_fields = (
        "level",
        "message",
    )
    list_display = (
        "pk",
        "level",
        "short_message",
        "time",
    )

    def delete_all_logs(modeladmin, request, queryset):
        DBLogEntry.objects.all().delete()

    actions = (delete_all_logs,)
