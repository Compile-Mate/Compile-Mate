from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'contests'

urlpatterns = [
    # Contest list and details
    path('', views.contest_list, name='contest_list'),
    path('<slug:slug>/', views.contest_detail, name='contest_detail'),
    path('<slug:slug>/register/', login_required(views.contest_register), name='contest_register'),
    # The following are not yet implemented as function-based views:
    # path('<slug:slug>/participate/', login_required(views.ContestParticipateView.as_view()), name='contest_participate'),
    
    # Contest problems
    path('<slug:slug>/problems/', login_required(views.contest_problems), name='contest_problems'),
    # path('<slug:slug>/problems/<int:problem_id>/', login_required(views.ContestProblemView.as_view()), name='contest_problem'),
    
    # Leaderboard
    path('<slug:slug>/leaderboard/', views.contest_leaderboard, name='contest_leaderboard'),
    # path('<slug:slug>/announcements/', views.ContestAnnouncementsView.as_view(), name='contest_announcements'),
    # path('<slug:slug>/results/', views.ContestResultsView.as_view(), name='contest_results'),
] 