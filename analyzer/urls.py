from django.urls import path, include
from rest_framework import routers
from .views import source_to_agency_id


urlpatterns = [
    path('source_to_agenci_id/', source_to_agency_id),
]
