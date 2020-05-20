from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import News
from agency.models import Agency
# Create your views here.

@api_view(['GET'])
def source_to_agency_id(self, version):
    without_agency_id = News.objects.all()
    print(without_agency_id.count())
    x = Agency.objects.all().values('id', 'name')
    print(x)
    for item in without_agency_id[:]:
        if item.source == '1':
            item.source = 'BBC'
        if item.source == '4':
            item.source = 'Euronews'
        if item.source == 'Foxnews':
            item.source = 'Fox News'
        if item.source == 'cnn' or item.source == '2':
            item.source = 'CNN'
        if item.source == 'france24':
            item.source = 'France24'
        if item.source == 'AP':
            item.source = 'Associated Press'
        if item.source == 'Asharq Al-Awsat' or item.source == 'AL-AWSAT' or item.source == '3':
            item.source = 'Asharq Al-awsat'
        if item.source == 'Times of Israel':
            item.source = 'The Times of Israel'
        if x.filter(name=item.source).count() > 0:
            item.agency_id = x.filter(name=item.source).first()['id']
            item.save()
        else:
            # unrecognized item source
            print(item.source)
    print('done')
    return Response({"msg":"ok"})