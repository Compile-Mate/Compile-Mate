from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from . import ai_views
from .views import ProfileView

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('profile/', login_required(ProfileView.as_view()), name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    
    # Support Chat URLs
    path('support/', login_required(views.support_chat_list), name='support_chat_list'),
    path('support/create/', login_required(views.create_support_chat), name='create_support_chat'),
    path('support/<int:chat_id>/', login_required(views.support_chat_detail), name='support_chat_detail'),
    path('support/<int:chat_id>/rate/', login_required(views.rate_chat), name='rate_chat'),
    path('support/<int:chat_id>/messages/', views.ChatMessageAPIView.as_view(), name='chat_messages'),
    path('support/templates/', login_required(views.chat_templates), name='chat_templates'),
    
    # Admin Support URLs
    path('admin/support/', login_required(views.admin_chat_dashboard), name='admin_chat_dashboard'),
    path('admin/support/chats/', login_required(views.admin_chat_list), name='admin_chat_list'),
    path('admin/support/<int:chat_id>/', login_required(views.admin_chat_detail), name='admin_chat_detail'),
    path('admin/support/<int:chat_id>/assign/', login_required(views.admin_assign_chat), name='admin_assign_chat'),
    path('admin/support/<int:chat_id>/resolve/', login_required(views.admin_resolve_chat), name='admin_resolve_chat'),
    
    # AI Features
    path('ai/tutor/', login_required(ai_views.ai_tutor_dashboard), name='ai_tutor_dashboard'),
    path('ai/get-hint/', login_required(ai_views.ai_get_hint), name='ai_get_hint'),
    path('ai/explain-error/', login_required(ai_views.ai_explain_error), name='ai_explain_error'),
    path('ai/review-code/', login_required(ai_views.ai_review_code), name='ai_review_code'),
    path('ai/suggest-tests/', login_required(ai_views.ai_suggest_test_cases), name='ai_suggest_test_cases'),
    path('ai/generate-problem/', login_required(ai_views.ai_generate_problem), name='ai_generate_problem'),
    path('ai/problem-generator/', login_required(ai_views.ai_problem_generator_page), name='ai_problem_generator_page'),
] 