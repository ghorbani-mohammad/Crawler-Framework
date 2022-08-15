from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

urlpatterns = [
    path("secret-admin/", admin.site.urls),
    re_path("api/(?P<version>(v1|v2))/", include("agency.urls")),
]

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.site_header = "Crawler Django Administration Panel"
admin.site.index_title = "Crawler"
admin.site.site_title = "Crawler Django Admin"
