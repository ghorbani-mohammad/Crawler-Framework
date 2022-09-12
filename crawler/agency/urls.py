from django.urls import path, include
from rest_framework import routers

from agency import views

router = routers.DefaultRouter()
router.register("agency", views.AgencyView)
router.register("page", views.PageView)
router.register("report", views.ReportView, basename="crawlreport")

urlpatterns = [
    path("", include(router.urls)),
    path("agency/<int:agency_id>/pages/", views.agency_pages),
    path("crawl/", views.crawl),
    path("crawl/page/<int:page_id>/", views.crawl_page),
    path("fetch_links/", views.FetchLinks.as_view()),
    path("test_error/", views.TestErrorView.as_view()),
    path("fetch_content/", views.FetchContent.as_view()),
    path("crawl/agency/active_all/", views.crawl_agency_activeAll),
    path("crawl/agency/disable_all/", views.crawl_agency_disableAll),
    path("crawl/agency/<int:agency_id>/", views.crawl_agency),
    path("crawl/memory/reset/", views.crawl_memory_reset),
    path("crawl/memory/reset/<int:agency_id>/", views.crawl_agency_reset_memory),
    path("crawl/news/memory/list/", views.crawl_news_memory_list),
    path("crawl/links/memory/list/", views.crawl_links_memory_list),
    path(
        "crawl/agency/reset_and_crawl/<int:agency_id>/",
        views.crawl_agency_reset_memory_and_crawl,
    ),
]
