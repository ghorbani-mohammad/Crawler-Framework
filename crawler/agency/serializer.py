from rest_framework import serializers
from agency.models import Agency, Report, Page
from rest_framework.fields import CharField


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
            "id",
            "name",
            "country",
            "website",
            "alexa_global_rank",
            "crawl_headers",
            "status",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class CrawlReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "page",
            "fetched_links",
            "new_links",
            "last_crawl_status",
            "created_at",
            "updated_at",
        ]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id",
            "agency",
            "url",
            "crawl_interval",
            "last_crawl",
            "status",
            "structure",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class ReportListSerializer(serializers.ModelSerializer):
    page = CharField(read_only=True, source="page.url")
    agency = CharField(read_only=True, source="page.agency.name")
    duration = serializers.SerializerMethodField("is_named_bar")

    def is_named_bar(self, obj):
        x = round((obj.updated_at - obj.created_at).total_seconds())
        return f"{x} sec"

    class Meta:
        model = Report
        fields = [
            "id",
            "page",
            "agency",
            "duration",
            "fetched_links",
            "new_links",
            "status",
            "created_at",
            "updated_at",
            "log",
        ]
