from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'judge'

urlpatterns = [
    # Code execution
    path('submit/', views.SubmitCodeView.as_view(), name='submit_code'),
    # path('run/', login_required(views.RunCodeView.as_view()), name='run_code'),
    # path('status/<str:judge_id>/', views.SubmissionStatusView.as_view(), name='submission_status'),
    
    # Language support
    # path('languages/', views.LanguageListView.as_view(), name='language_list'),
    # path('languages/<str:language>/template/', views.LanguageTemplateView.as_view(), name='language_template'),
] 