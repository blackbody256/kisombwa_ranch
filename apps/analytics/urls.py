from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),  # /analytics/
    path('dashboard/', views.analytics_dashboard, name='dashboard_alt'),  # /analytics/dashboard/
    path('export/', views.export_report, name='export_report'),  # /analytics/export/
]
