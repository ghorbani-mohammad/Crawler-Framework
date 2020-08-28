from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('api/(?P<version>(v1|v2))/', include('agency.urls')),
]

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.site_header = "Crawler"
admin.site.site_title = "Crawler"


urlpatterns += staticfiles_urlpatterns()
