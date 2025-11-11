"""
URL Configuration for Daily Challenges App
"""

from django.urls import path
from . import views

app_name = 'daily_challenges'

urlpatterns = [
    path('', views.daily_challenge, name='daily_challenge'),
    path('start/', views.start_challenge, name='start_challenge'),
    path('complete/', views.complete_challenge, name='complete_challenge'),
    path('history/', views.challenge_history, name='challenge_history'),
    path('leaderboard/', views.streak_leaderboard, name='streak_leaderboard'),
    path('freeze-shop/', views.streak_freeze_shop, name='streak_freeze_shop'),
    path('freeze/purchase/', views.purchase_streak_freeze, name='purchase_streak_freeze'),
    path('freeze/use/', views.use_streak_freeze, name='use_streak_freeze'),
]

