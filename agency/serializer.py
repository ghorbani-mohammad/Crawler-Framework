from rest_framework import serializers
from agency.models import Agency, CrawlReport, AgencyPageStructure


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
                    'name',
                    'website',
                    'crawl_interval',
                    'status',
                    'number_of_crawls',
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
        ]

class AgencyPageStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyPageStructure
        fields = [
                    'agency',
                    'page',
                    'structure',
        ]