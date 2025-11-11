from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
# from . import views

app_name = 'rewards'

def marketplace(request):
    return render(request, 'rewards/marketplace.html')

def user_rewards_placeholder(request):
    """Placeholder view for user rewards until it's fully implemented."""
    return render(request, 'rewards/marketplace_placeholder.html', {
        'title': 'My Rewards',
        'message': 'Your rewards dashboard is coming soon! You\'ll be able to view your MateCoins, achievements, and redemption history.'
    })

urlpatterns = [
    # Marketplace
    path('marketplace/', marketplace, name='marketplace'),
    # path('vouchers/', views.VoucherListView.as_view(), name='voucher_list'),
    # path('vouchers/<int:pk>/', views.VoucherDetailView.as_view(), name='voucher_detail'),
    # path('vouchers/<int:pk>/redeem/', login_required(views.VoucherRedeemView.as_view()), name='voucher_redeem'),
    
    # User rewards
    path('my-rewards/', login_required(user_rewards_placeholder), name='user_rewards'),
    # path('transactions/', login_required(views.TransactionHistoryView.as_view()), name='transaction_history'),
    
    # Daily rewards
    # path('daily/', login_required(views.DailyRewardView.as_view()), name='daily_reward'),
    
    # Referrals
    # path('referrals/', login_required(views.ReferralView.as_view()), name='referrals'),
] 