from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/livestock/', permanent=False)),  # Add this line
    path('admin/', admin.site.urls),
    path('livestock/', include('apps.livestock.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('ai-insights/', include('apps.ai_insights.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('iot/', include('apps.iot.urls')),
    path('', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)