from rest_framework import serializers
from rest_framework.fields import CharField

from . import models


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Agency
        fields = [
            "id",
            "name",
            "status",
            "country",
            "website",
            "created_at",
            "updated_at",
            "deleted_at",
            "crawl_headers",
        ]


class CrawlReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Report
        fields = [
            "id",
            "page",
            "new_links",
            "created_at",
            "updated_at",
            "fetched_links",
            "last_crawl_status",
        ]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Page
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
        model = models.Report
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
