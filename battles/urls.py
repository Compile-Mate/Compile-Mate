"""
URL Configuration for Battles App
"""

from django.urls import path
from . import views

app_name = 'battles'

urlpatterns = [
    path('', views.battle_list, name='battle_list'),
    path('create/', views.create_battle, name='create_battle'),
    path('<uuid:battle_id>/', views.battle_arena, name='battle_arena'),
    path('<uuid:battle_id>/join/', views.join_battle, name='join_battle'),
    path('invitation/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitation/<int:invitation_id>/decline/', views.decline_invitation, name='decline_invitation'),
    path('history/', views.battle_history, name='battle_history'),
    path('leaderboard/', views.leaderboard, name='battle_leaderboard'),
]

