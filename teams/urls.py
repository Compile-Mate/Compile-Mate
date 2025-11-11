from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='list'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('create/', views.create_team, name='create_team'),
    path('<int:team_id>/join/', views.join_team, name='join_team'),
    path('<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('<int:team_id>/invite/', views.invite_member, name='invite_member'),
    path('invitation/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitation/<int:invitation_id>/decline/', views.decline_invitation, name='decline_invitation'),
]

