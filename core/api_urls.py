from django.urls import path
from . import api_views

app_name = 'core_api'

urlpatterns = [
    # User API endpoints
    path('user/profile/', api_views.UserProfileAPIView.as_view(), name='user_profile'),
    path('user/stats/', api_views.UserStatsAPIView.as_view(), name='user_stats'),
    path('user/notifications/', api_views.NotificationAPIView.as_view(), name='notifications'),
    
    # Site API endpoints
    path('site/settings/', api_views.SiteSettingsAPIView.as_view(), name='site_settings'),
    path('site/leaderboard/', api_views.LeaderboardAPIView.as_view(), name='leaderboard'),
    
    # Utility endpoints
    path('search/', api_views.SearchAPIView.as_view(), name='search'),
] 