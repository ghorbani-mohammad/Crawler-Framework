import redis
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from agency.models import Agency, AgencyPageStructure, CrawlReport
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer, CrawlReportSerializer
from app.messages import *

class AgencyView(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer

class PageView(viewsets.ModelViewSet):
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

# @api_view(['GET'])
class ReportView(viewsets.ModelViewSet):
    queryset = CrawlReport.objects.all()
    serializer_class = CrawlReportSerializer

