"""
URL configuration for compilemate project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', include('core.api_urls')),
    path('problems/', include('problems.urls')),
    path('contests/', include('contests.urls')),
    path('rewards/', include('rewards.urls')),
    path('judge/', include('judge.urls')),
    path('resume/', include('resume_scanner.urls', namespace='resume_scanner')),
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False)),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("browser-reload/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 