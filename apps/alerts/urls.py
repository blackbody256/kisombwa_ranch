from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.alerts_dashboard, name='dashboard'),
    path('<uuid:alert_id>/read/', views.mark_alert_read, name='mark_read'),
    path('<uuid:alert_id>/resolve/', views.resolve_alert, name='resolve'),
    path('generate/', views.generate_alerts, name='generate'),
]
