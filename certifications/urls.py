from django.urls import path
from . import views

app_name = 'certifications'

urlpatterns = [
    path('', views.certificate_list, name='list'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),
    path('certificate/<slug:slug>/', views.certificate_detail, name='detail'),
    path('download/<int:certificate_id>/', views.download_certificate, name='download'),
    path('verify/<uuid:certificate_id>/', views.verify_certificate, name='verify'),
]

