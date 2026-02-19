from django.urls import path
from . import views

app_name = 'ai_insights'

urlpatterns = [
    path('', views.ai_insights_dashboard, name='dashboard'),
    path('dashboard/', views.ai_insights_dashboard, name='dashboard_alt'),
]
