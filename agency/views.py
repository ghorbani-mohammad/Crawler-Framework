import redis
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from agency.models import Agency, AgencyPageStructure
from agency.serializer import AgencySerializer, AgencyPageStructureSerializer
from app.messages import *


@csrf_exempt
def agency_list(request, version):
    if version == "v1":
        if request.method == 'GET':
            agencies = Agency.objects.all()
            serializer = AgencySerializer(agencies, many=True)
            return JsonResponse(serializer.data, safe=False)
        elif request.method == 'POST':
            data = JSONParser().parse(request)
            serializer = AgencySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse({'status':'error', 'msg': serializer.errors})
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)

@csrf_exempt
def agency_detail(request, agency_id, version):
    try:
        agency = Agency.objects.get(id=agency_id)
    except Agency.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'agency does not found'}, status=404)

    if request.method == 'GET':
        serializer = AgencySerializer(agency)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        data['id'] = agency_id
        serializer = AgencySerializer(agency, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=202)
        return JsonResponse({'statue': 'error', 'msg': serializer.errors}, status=400)

    elif request.method == 'DELETE':
        agency.delete()
        return HttpResponse(status=202)


@csrf_exempt
def page_structure(request, agency_id, version):
    if version == "v1":
        if request.method == 'GET':
            page_structures = AgencyPageStructure.objects.filter(agency=agency_id)
            serializer = AgencyPageStructureSerializer(page_structures, many=True)
            return JsonResponse(serializer.data, safe=False)
        elif request.method == 'POST':
            data = JSONParser().parse(request)
            data['agency'] = agency_id
            serializer = AgencyPageStructureSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse({'status':'error', 'msg': serializer.errors})
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)

@csrf_exempt
def page_structure_detail(request, agency_id, page_id, version):
    if version == "v1":
        try:
            page_structure = AgencyPageStructure.objects.get(id=page_id)
        except Agency.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'page structure does not found'}, status=404)

        if request.method == 'GET':
            serializer = AgencyPageStructureSerializer(page_structure)
            return JsonResponse(serializer.data, safe=False)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            data['agency'] = agency_id
            serializer = AgencyPageStructureSerializer(page_structure, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=202)
            return JsonResponse({'statue': 'error', 'msg': serializer.errors}, status=400)

        elif request.method == 'DELETE':
            page_structure.delete()
            return HttpResponse(status=202)
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)


def crawl(request, version):
    AgencyPageStructure.objects.all().update(last_crawl=None)
    return JsonResponse({'status':'ok', 'msg': msg['fa']['crawl']['success_crawl_all']})

def crawl_page(request, version, page_id):
    AgencyPageStructure.objects.filter(id=page_id).update(last_crawl=None)
    return JsonResponse({'status':'ok', 'msg': msg['fa']['crawl']['success_crawl_page']})

def crawl_agency(request, version, agency_id):
    AgencyPageStructure.objects.filter(agency=agency_id).update(last_crawl=None)
    return JsonResponse({'status':'ok', 'msg':msg['fa']['crawl']['success_crawl_agency']})


def crawl_memory_reset(request,version):
    redis_news = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_duplicate_checker = redis.StrictRedis(host='localhost', port=6379, db=1)
    redis_duplicate_checker.flushall()
    redis_news.flushall()
    return JsonResponse({'status': 'ok', 'msg': msg['fa']['crawl']['success_crawl_memory_reset']}, status=200)