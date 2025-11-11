from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listings
    path('', views.job_list, name='list'),
    path('job/<slug:slug>/', views.job_detail, name='job_detail'),
    path('job/<slug:slug>/apply/', views.apply_job, name='apply_job'),
    
    # Applications
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Companies
    path('companies/', views.companies_list, name='companies_list'),
    path('company/<slug:slug>/', views.company_detail, name='company_detail'),
]

