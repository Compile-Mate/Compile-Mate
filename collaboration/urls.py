from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('', views.room_list, name='list'),
    path('create/', views.create_room, name='create'),
    path('room/<uuid:room_id>/', views.room_view, name='room'),
    path('room/<uuid:room_id>/leave/', views.leave_room, name='leave'),
]

