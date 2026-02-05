from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/livestock/', permanent=False)),  # Add this line
    path('admin/', admin.site.urls),
    path('livestock/', include('apps.livestock.urls')),
    # Add other app URLs here later (iot, analytics, alerts)
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)