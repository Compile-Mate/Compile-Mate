from django.urls import path
from . import views

app_name = 'snippets'

urlpatterns = [
    path('', views.snippet_list, name='list'),
    path('create/', views.snippet_create, name='create'),
    path('<int:snippet_id>/', views.snippet_detail, name='detail'),
    path('<int:snippet_id>/delete/', views.snippet_delete, name='delete'),
]

