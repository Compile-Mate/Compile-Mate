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
    
    # New feature apps
    path('battles/', include('battles.urls', namespace='battles')),
    path('daily-challenge/', include('daily_challenges.urls', namespace='daily_challenges')),
    path('achievements/', include('achievements.urls', namespace='achievements')),
    path('teams/', include('teams.urls', namespace='teams')),
    path('reviews/', include('code_reviews.urls', namespace='code_reviews')),
    path('feed/', include('social_feed.urls', namespace='social_feed')),
    path('learn/', include('learning_paths.urls', namespace='learning_paths')),
    path('snippets/', include('snippets.urls', namespace='snippets')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('certificates/', include('certifications.urls', namespace='certifications')),
    path('collaborate/', include('collaboration.urls', namespace='collaboration')),
    
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False)),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        # path("__debug__/", include("debug_toolbar.urls")),  # Disabled due to psycopg compatibility issue
        path("browser-reload/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 