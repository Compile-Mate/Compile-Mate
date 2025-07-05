from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import CoinTransaction, UserAchievement
from .models import VoucherRedemption, UserReward, DailyReward, ReferralReward

@login_required
def user_rewards_dashboard(request):
    user = request.user
    # MateCoins and XP
    coins = user.coins
    xp = user.xp
    level = user.level
    # Achievements
    achievements = UserAchievement.objects.filter(user=user).order_by('-earned_at')
    # Earned rewards (badges, titles, etc.)
    earned_rewards = UserReward.objects.filter(user=user).select_related('reward', 'reward__category').order_by('-earned_at')
    # Voucher redemptions
    voucher_redemptions = VoucherRedemption.objects.filter(user=user).select_related('voucher').order_by('-redeemed_at')
    # Coin transactions
    coin_transactions = CoinTransaction.objects.filter(user=user).order_by('-timestamp')[:20]
    # Daily rewards
    daily_rewards = DailyReward.objects.filter(user=user).order_by('-date')[:10]
    # Referral rewards
    referral_rewards = ReferralReward.objects.filter(referrer=user).select_related('referred_user').order_by('-created_at')

    context = {
        'user': user,
        'coins': coins,
        'xp': xp,
        'level': level,
        'achievements': achievements,
        'earned_rewards': earned_rewards,
        'voucher_redemptions': voucher_redemptions,
        'coin_transactions': coin_transactions,
        'daily_rewards': daily_rewards,
        'referral_rewards': referral_rewards,
    }
    return render(request, 'rewards/user_rewards.html', context) 