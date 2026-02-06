from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.livestock_home, name='livestock_home'),
    path('animals/', views.animal_list, name='animal_list'),
    path('register/', views.animal_register, name='animal_register'),
    
    # QR Scanner
    path('scan/', views.qr_scanner, name='qr_scanner'),
    
    # Animal profile (loads after QR scan)
    path('animal/<str:tag_id>/', views.animal_profile, name='animal_profile'),
    
    # Add records
    path('health/add/', views.health_record_add, name='health_record_add'),
    path('health/add/<str:tag_id>/', views.health_record_add, name='health_record_add_for_animal'),
    
    path('vaccination/add/', views.vaccination_add, name='vaccination_add'),
    path('vaccination/add/<str:tag_id>/', views.vaccination_add, name='vaccination_add_for_animal'),
    
    path('weight/add/', views.weight_record_add, name='weight_record_add'),
    path('weight/add/<str:tag_id>/', views.weight_record_add, name='weight_record_add_for_animal'),
]