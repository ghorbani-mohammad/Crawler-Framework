from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from agency.models import Agency
from agency.serializer import AgencySerializer


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
def agency_detail(request, id, version):
    if version == "v1":
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'msg': 'version is not defined'}, status=404)