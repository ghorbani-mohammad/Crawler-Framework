from django.urls import path
from agency import views

urlpatterns = [
    path('agency/', views.agency_list),
    path('agency/<int:agency_id>/', views.agency_detail),
    path('agency/<int:agency_id>/pagestructure/', views.page_structure),
    path('agency/<int:agency_id>/pagestructure/<int:page_id>/', views.page_structure_detail),
    path('crawl/', views.crawl),
    path('crawl/page/<int:page_id>', views.crawl_page),
    path('crawl/agency/<int:agency_id>', views.crawl_agency),
    path('crawl/memory/reset', views.crawl_memory_reset),

]
