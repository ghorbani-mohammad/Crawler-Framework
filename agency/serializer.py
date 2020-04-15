from rest_framework import serializers
from agency.models import Agency, CrawlReport, AgencyPageStructure


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
                    'id',
                    'name',
                    'website',
                    'crawl_headers',
                    'status',
                    'created_at',
                    'updated_at',
        ]

class CrawlReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlReport
        fields = [
                    'agency',
                    'last_crawl',
                    'last_crawl_duration',
                    'last_crawl_status',
                    'created_at',
                    'updated_at',
        ]

class AgencyPageStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyPageStructure
        fields = [
                    'id',
                    'agency',
                    'url',
                    'crawl_interval',
                    'last_crawl',
                    'news_links_structure',
                    'news_meta_structure',
                    'created_at',
                    'updated_at',
        ]