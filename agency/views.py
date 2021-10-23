import redis, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import NotAcceptable

from agency.serializer import AgencySerializer, AgencyPageStructureSerializer, CrawlReportSerializer, \
    ReportListSerializer
from agency.models import Agency, Page, Report
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer, ReportListSerializer
from agency.models import Agency
# from agency.models import AgencyPageStructure, CrawlReport
from app.messages import *
from app import tasks


class PostPagination(PageNumberPagination):
    page_size = 10


class AgencyView(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            response_data = {
                "status": "200",
                "message": msg['fa']['agency']['success_agency_created'],
                "data": serializer.data
            }
            tasks.fetch_alexa_rank.delay(serializer.data['id'], serializer.data['website'])
            print(serializer.data['id'], serializer.data['website'])
        else:
            response_data = {
                "status": "400",
                "message": msg['fa']['agency']['failed_agency_created'],
                "data": serializer.errors
            }
        return Response(response_data)

    def update(self, request, version, pk=None):
        try:
            instance = self.queryset.get(pk=pk)
        except:
            return Response({'status':'400', 'message': msg['fa']['agency']['agency_not_found']})
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "200",
                "message": msg['fa']['agency']['success_agency_updated'],
                "data": serializer.data
            }
            tasks.fetch_alexa_rank.delay(serializer.data['id'], serializer.data['website'])
        else:
            response_data = {
                "status": "400",
                "message": msg['fa']['agency']['failed_agency_updated'],
                "data": serializer.errors
            }
        return Response(response_data)
    
    def retrieve(self, request, version, pk=None):
        try:
            agency = Agency.objects.get(pk=pk)
        except Agency.DoesNotExist:
            return Response({'status':'400', 'message':msg['fa']['agency']['agency_not_found']})
        serializer = AgencySerializer(agency)
        x = {}
        x['status'] = '200'
        x['message'] = msg['fa']['agency']['agency_found']
        x['data'] = serializer.data
        return Response(x)
    
    def destroy(self, request, version, pk=None):
        try:
            agency = Agency.objects.get(pk=pk)
        except Agency.DoesNotExist:
            return Response({'status':'400', 'message':msg['fa']['agency']['agency_not_found']})
        agency.deleted_at= datetime.datetime.now()
        agency.save()
        response_data = {
            "status": "200",
            "message": msg['fa']['agency']['success_agency_deleted'],
            "data": ""
        }
        return Response(response_data)

    queryset = Agency.objects.filter(deleted_at=None).order_by('id')
    serializer_class = AgencySerializer


class PageView(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
        except:
            response_data = {
                "status": "400",
                "message": msg['fa']['page']['failed_page_created'],
                "data": msg['fa']['app']['json_validation_error']
            }
            return Response(response_data)
        if serializer.is_valid():
            self.perform_create(serializer)
            response_data = {
                "status": "200",
                "message": msg['fa']['page']['success_page_created'],
                "data": serializer.data
            }
        else:
            response_data = {
                "status": "400",
                "message": msg['fa']['page']['failed_page_created'],
                "data": serializer.errors
            }
        return Response(response_data)
    
    def retrieve(self, request, version, pk=None):
        try:
            page = Page.objects.get(pk=pk)
        except Page.DoesNotExist:
            return Response({'status':'400', 'message':msg['fa']['page']['page_not_found']})
        serializer = AgencyPageStructureSerializer(page)
        x = {}
        x['status'] = '200'
        x['message'] = msg['fa']['page']['page_found']
        x['data'] = serializer.data
        return Response(x)

    def update(self, request, version, pk=None):
        try:
            instance = self.queryset.get(pk=pk)
        except:
            return Response({'status':'400', 'message': msg['fa']['page']['page_not_found']})

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "200",
                "message": msg['fa']['page']['success_page_updated'],
                "data": serializer.data
            }
        else:
            response_data = {
                "status": "400",
                "message": msg['fa']['page']['failed_page_updated'],
                "data": serializer.errors
            }
        return Response(response_data)

    def destroy(self, request, version, pk=None):
        try:
            page = Page.objects.get(pk=pk)
        except Page.DoesNotExist:
            return Response({'status':'400', 'message':msg['fa']['page']['page_not_found']})
        page.deleted_at=datetime.datetime.now()
        page.save()
        response_data = {
            "status": "200",
            "message": msg['fa']['page']['success_page_deleted'],
            "data": ""
        }
        return Response(response_data)
    
    # pagination_class = PostPagination
    queryset = Page.objects.all().order_by('id')
    # queryset = AgencyPageStructure.objects.filter(deleted_at=None).order_by('id')
    serializer_class = AgencyPageStructureSerializer

@api_view(['GET'])
def agency_pages(request, version, agency_id):
    pages = Page.objects.filter(agency_id=agency_id)
    serializer = AgencyPageStructureSerializer(pages, many=True)
    x = {}
    x['status'] = '200'
    x['message'] = msg['fa']['agency']['retrieved_pages']
    x['data'] = serializer.data
    return Response(x)

@api_view(['GET'])
def crawl(request, version):
    Page.objects.all().update(last_crawl=None)
    return Response({'status':'200', 'message': msg['fa']['crawl']['success_crawl_all']})

@api_view(['GET'])
def crawl_page(request, version, page_id):
    Page.objects.filter(id=page_id).update(last_crawl=None)
    return Response({'status':'200', 'message': msg['fa']['crawl']['success_crawl_page']})

@api_view(['GET'])
def crawl_agency_activeAll(request, version):
    Agency.objects.update(status=True)
    return Response({'status':'200', 'message':msg['fa']['crawl']['success_crawl_agency_activeAll']})

@api_view(['GET'])
def crawl_agency_disableAll(request, version):
    Agency.objects.update(status=False)
    return Response({'status':'200', 'message':msg['fa']['crawl']['success_crawl_agency_disableAll']})

def crawl_agency_none_lats_crawl(agency_id):
    Agency.objects.filter(id=agency_id).update(status=True)
    Page.objects.filter(agency=agency_id).update(last_crawl=None, status=True)
    x = Page.objects.filter(agency=agency_id).values('id')
    x = Report.objects.filter(page__in=x, status='pending').update(status='failed')
    

@api_view(['GET'])
def crawl_agency(request, version, agency_id):
    crawl_agency_none_lats_crawl(agency_id)
    return Response({'status':'200', 'message':msg['fa']['crawl']['success_crawl_agency']})

@api_view(['GET'])
def crawl_memory_reset(request,version):
    redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
    redis_duplicate_checker = redis.StrictRedis(host='crawler_redis', port=6379, db=1)
    redis_duplicate_checker.flushall()
    redis_news.flushall()
    return JsonResponse({'status': '200', 'message': msg['fa']['crawl']['success_crawl_memory_reset']}, status=200)

@api_view(['GET'])
def crawl_news_memory_list(request, version):
    redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
    return Response({'news_keys':redis_news.keys("*")})

@api_view(['GET'])
def crawl_links_memory_list(request, version):
    redis_duplicate_checker = redis.StrictRedis(host='crawler_redis', port=6379, db=1)
    return Response({'link_keys':redis_duplicate_checker.keys("*")})

def reset_agency_memory(agency_id):
    agency = Agency.objects.get(id=agency_id)
    redis_news = redis.StrictRedis(host='crawler_redis', port=6379, db=0)
    redis_duplicate_checker = redis.StrictRedis(host='crawler_redis', port=6379, db=1)
    counter_links = 0 
    for key in redis_duplicate_checker.scan_iter("*"+str(agency.website)+"*"):
        redis_duplicate_checker.delete(key)
        counter_links += 1
    counter_news = 0
    for key in redis_news.scan_iter("*"+str(agency.website)+"*"):
        redis_news.delete(key)
        counter_news += 1
    return counter_links, counter_news

@api_view(['GET'])
def crawl_agency_reset_memory(request, version, agency_id):
    counter_links, counter_news = reset_agency_memory(agency_id)
    return Response({'number_of_links_deleted':counter_links, 'number_of_news_deleted': counter_news})


@api_view(['GET'])
def crawl_agency_reset_memory_and_crawl(request, version, agency_id):
    crawl_agency_none_lats_crawl(agency_id)
    counter_links, counter_news = reset_agency_memory(agency_id)
    return Response({'number_of_links_deleted':counter_links, 'number_of_news_deleted': counter_news})



class ReportView(ReadOnlyModelViewSet):
    pagination_class = PostPagination
    def list(self, request, version):
        queryset = Report.objects.all()
        # page = self.paginate_queryset(queryset)
        # serializer = ReportListSerializer(page, many=True)
        # x = {}
        # x['status'] = '200'
        # x['message'] = msg['fa']['report']['report_found']
        # x['data'] = serializer.data
        # return self.get_paginated_response(serializer.data)
        serializer = ReportListSerializer(queryset, many=True)
        return Response(serializer.data)
        # queryset = CrawlReport.objects.all().order_by('-id')
        # page = self.paginate_queryset(queryset)
        # serializer = ReportListSerializer(page, many=True)
        # x = {}
        # x['status'] = '200'
        # x['message'] = msg['fa']['report']['report_found']
        # x['data'] = serializer.data
        # return self.get_paginated_response(serializer.data)

    def retrieve(self, request, version, pk=None):
        queryset = Report.objects.all()
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'status':'418', 'message':msg['fa']['report']['report_not_found']})
        serializer = ReportListSerializer(report)
        x = {}
        x['status'] = '200'
        x['message'] = msg['fa']['report']['report_found']
        x['data'] = serializer.data
        return Response(x)


# class FetchLinks(APIView):
#     def get(self, request, version):
#         from agency.crawler_engine import CrawlerEngineV2
#         page_id = request.GET.get('page_id', None)
#         if page_id is None:
#             raise NotAcceptable(detail='page_id is not acceptable')
#         page = get_object_or_404(AgencyPageStructure, pk=page_id)
#         crawler = CrawlerEngineV2()
#         links = crawler.get_links(page.news_links_structure, page.url)
#         return Response({'count': len(links), 'links': links})


# class FetchContent(APIView):
#     def get(self, request, version):
#         from agency.crawler_engine import CrawlerEngineV2
#         link = request.GET.get('link', None)
#         page_id = request.GET.get('page_id', None)
#         if link is None or page_id is None:
#             raise NotAcceptable(detail='link or page_id is not acceptable')
#         page = get_object_or_404(AgencyPageStructure, pk=page_id)
#         crawler = CrawlerEngineV2()
#         content = crawler.get_content(page.news_meta_structure, link)
#         return Response({'page': page.id, 'content': content})   