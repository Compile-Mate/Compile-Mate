from django.urls import path
from . import views

app_name = 'code_reviews'

urlpatterns = [
    path('', views.review_list, name='list'),
    path('request/', views.request_review, name='request'),
    path('<int:review_id>/', views.review_detail, name='detail'),
]

