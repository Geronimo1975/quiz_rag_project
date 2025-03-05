from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),
    path('accounts/', include('accounts.urls')),
    path('rag/', include('rag.urls')),
    # Add this line to include teacher_dashboard URLs
    path('teacher/', include('teacher_dashboard.urls')),
    path('', RedirectView.as_view(url='quiz/', permanent=False)),
]

# Add this for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
