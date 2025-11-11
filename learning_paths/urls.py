from django.urls import path
from . import views

app_name = 'learning_paths'

urlpatterns = [
    path('', views.path_list, name='list'),
    path('my-paths/', views.my_paths, name='my_paths'),
    path('<slug:slug>/', views.path_detail, name='detail'),
    path('<slug:slug>/enroll/', views.enroll_path, name='enroll'),
]

