from rest_framework import serializers
from agency.models import Agency, CrawlReport, Page
from rest_framework.fields import CharField


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
                    'id',
                    'name',
                    'country',
                    'website',
                    'alexa_global_rank',
                    'crawl_headers',
                    'status',
                    'created_at',
                    'updated_at',
        ]


class CrawlReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlReport
        fields = [
                    'id',
                    'page',
                    'fetched_links',
                    'new_links',
                    'last_crawl_status',
                    'created_at',
                    'updated_at',
        ]


class AgencyPageStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
                    'id',
                    'agency',
                    'url',
                    'crawl_interval',
                    'last_crawl',
                    'status',
                    'news_links_structure',
                    'news_meta_structure',
                    'created_at',
                    'updated_at',
        ]


class ReportListSerializer(serializers.ModelSerializer):
    page = CharField(read_only=True, source="page.url")
    agency = CharField(read_only=True, source="page.agency.name")
    duration = serializers.SerializerMethodField('is_named_bar')

    def is_named_bar(self, obj):
        x = round((obj.updated_at - obj.created_at).total_seconds())
        return "{} sec".format(x)

    class Meta:
        model = CrawlReport
        fields = [
            'id',
            'page',
            'agency',
            'duration',
            'fetched_links',
            'new_links',
            'status',
            'created_at',
            'updated_at',
        ]
