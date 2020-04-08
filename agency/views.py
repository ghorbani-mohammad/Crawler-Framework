from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from agency.models import Agency
from agency.serializer import AgencySerializer


@csrf_exempt
def agency_list(request, version):
    if version == "v1":
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)

@csrf_exempt
def agency_detail(request, id, version):
    if version == "v1":
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)