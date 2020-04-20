from django.urls import path, include
from rest_framework import routers
from agency import views

router = routers.DefaultRouter()
router.register('agency', views.AgencyView)
router.register('page', views.PageView)
router.register('report', views.ReportView)

urlpatterns = [
    path('', include(router.urls)),
    path('agency/<int:agency_id>/pages/', views.agency_pages),
    path('crawl/', views.crawl),
    path('crawl/page/<int:page_id>/', views.crawl_page),
    path('crawl/agency/<int:agency_id>/', views.crawl_agency),
    path('crawl/memory/reset/', views.crawl_memory_reset),
]
