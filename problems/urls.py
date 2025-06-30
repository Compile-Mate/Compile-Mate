from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'problems'

urlpatterns = [
    # Problem list and details
    path('', views.problem_list, name='problem_list'),
    
    # Submissions - these must come before the generic slug pattern
    path('submissions/', login_required(views.user_submissions), name='submission_list'),
    path('submissions/<int:submission_id>/', login_required(views.submission_detail), name='submission_detail'),
    
    # Problem-specific paths
    path('<slug:slug>/', views.problem_detail, name='problem_detail'),
    path('<slug:slug>/solve/', login_required(views.problem_solve), name='problem_solve'),
    path('<slug:slug>/submit/', login_required(views.submit_code), name='submit_code'),
    
    # The following are not yet implemented as function-based views:
    # path('<slug:slug>/discussions/', views.ProblemDiscussionView.as_view(), name='problem_discussions'),
    # path('discussions/<int:pk>/', views.DiscussionDetailView.as_view(), name='discussion_detail'),
    # path('tags/', views.TagListView.as_view(), name='tag_list'),
    # path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
] 