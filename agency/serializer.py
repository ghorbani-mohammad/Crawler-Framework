from rest_framework import serializers
from agency.models import Agency


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
                    'name',
                    'website',
                    'crawl_interval',
                    'status',
                    'last_crawl',
                    'last_crawl_duration',
                    'last_crawl_status',
                    'number_of_crawls',
                    'created',
                    'updated',
        ]