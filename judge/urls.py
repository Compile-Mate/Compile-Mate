from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'judge'

urlpatterns = [
    # Code execution
    path('submit/', views.SubmitCodeView.as_view(), name='submit_code'),
    
    # Submission status polling
    path('status/<int:submission_id>/', views.get_submission_status, name='submission_status'),
    
    # Quick test (no submission record)
    path('test/', views.quick_test, name='quick_test'),
    
    # Language support
    path('languages/', views.supported_languages, name='supported_languages'),
] 