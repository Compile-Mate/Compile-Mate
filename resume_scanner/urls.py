from django.urls import path
from . import views

app_name = 'resume_scanner'

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:scan_id>/', views.scan_result, name='scan_result'),
] 