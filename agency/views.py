import redis
from django.http import HttpResponse, JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from agency.models import Agency, AgencyPageStructure, CrawlReport
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer, CrawlReportSerializer, \
    ReportListSerializer
from app.messages import *
from rest_framework.viewsets import ReadOnlyModelViewSet


class PostPagination(PageNumberPagination):
    page_size = 10


class AgencyView(viewsets.ModelViewSet):
    pagination_class = PostPagination
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer


class PageView(viewsets.ModelViewSet):
    pagination_class = PostPagination
    queryset = AgencyPageStructure.objects.all()
    serializer_class = AgencyPageStructureSerializer

@api_view(['GET'])
def agency_pages(request, version, agency_id):
    pages = AgencyPageStructure.objects.filter(agency_id=agency_id)
    serializer = AgencyPageStructureSerializer(pages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def crawl(request, version):
    AgencyPageStructure.objects.all().update(last_crawl=None)
    return Response({'status':'ok', 'msg': msg['fa']['crawl']['success_crawl_all']})

@api_view(['GET'])
def crawl_page(request, version, page_id):
    AgencyPageStructure.objects.filter(id=page_id).update(last_crawl=None)
    return Response({'status':'ok', 'msg': msg['fa']['crawl']['success_crawl_page']})

@api_view(['GET'])
def crawl_agency(request, version, agency_id):
    AgencyPageStructure.objects.filter(agency=agency_id).update(last_crawl=None)
    return Response({'status':'ok', 'msg':msg['fa']['crawl']['success_crawl_agency']})

@api_view(['GET'])
def crawl_memory_reset(request,version):
    redis_news = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_duplicate_checker = redis.StrictRedis(host='localhost', port=6379, db=1)
    redis_duplicate_checker.flushall()
    redis_news.flushall()
    return JsonResponse({'status': 'ok', 'msg': msg['fa']['crawl']['success_crawl_memory_reset']}, status=200)


class ReportView(ReadOnlyModelViewSet):
    pagination_class = PostPagination
    queryset = CrawlReport.objects.all()
    serializers = {
        'list': ReportListSerializer,
        'retrieve': ReportListSerializer
    }
    def get_serializer_class(self):
        return self.serializers.get(self.action)

