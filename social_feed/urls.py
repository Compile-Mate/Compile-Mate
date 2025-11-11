from django.urls import path
from . import views

app_name = 'social_feed'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('user/<str:username>/', views.user_profile, name='profile'),
    path('user/<str:username>/follow/', views.follow_user, name='follow'),
]

