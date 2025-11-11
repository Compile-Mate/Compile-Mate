from django.urls import path
from . import views

app_name = 'achievements'

urlpatterns = [
    path('', views.achievement_list, name='list'),
    path('badges/', views.badge_showcase, name='badge_showcase'),
    path('milestones/', views.milestones, name='milestones'),
]

