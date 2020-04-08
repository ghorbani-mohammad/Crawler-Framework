from django.urls import path
from agency import views

urlpatterns = [
    path('agency/', views.agency_list),
    path('agency/<int:id>/', views.agency_detail),
]
