"""
Views for Daily Coding Challenges
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

from .models import (
    DailyChallenge, DailyChallengeParticipation, StreakStats,
    StreakFreezeItem, StreakFreezePurchase, DailyChallengeLeaderboard
)
from problems.models import Submission


@login_required
def daily_challenge(request):
    """Display today's daily challenge."""
    today = timezone.now().date()
    
    # Get or create today's challenge
    challenge = DailyChallenge.objects.get_today_challenge()
    
    # Check if user has already participated
    participation = DailyChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).first()
    
    # Get user's streak stats
    streak_stats, _ = StreakStats.objects.get_or_create(user=request.user)
    
    # Get today's leaderboard
    leaderboard = DailyChallengeLeaderboard.objects.filter(
        challenge=challenge
    ).select_related('user').order_by('rank')[:10]
    
    # Check if streak is at risk
    yesterday = today - timedelta(days=1)
    streak_at_risk = (
        streak_stats.last_completed_date and 
        streak_stats.last_completed_date < yesterday and
        streak_stats.current_streak > 0
    )
    
    context = {
        'challenge': challenge,
        'participation': participation,
        'streak_stats': streak_stats,
        'leaderboard': leaderboard,
        'streak_at_risk': streak_at_risk,
        'can_use_freeze': streak_stats.can_use_freeze(),
    }
    return render(request, 'daily_challenges/daily_challenge.html', context)


@login_required
@require_http_methods(["POST"])
def start_challenge(request):
    """Start today's challenge for the user."""
    challenge = DailyChallenge.objects.get_today_challenge()
    
    # Check if already started
    if DailyChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).exists():
        return JsonResponse({'error': 'Challenge already started'}, status=400)
    
    # Create participation
    participation = DailyChallengeParticipation.objects.create(
        user=request.user,
        challenge=challenge,
        status='started'
    )
    
    # Update challenge participant count
    challenge.participants_count += 1
    challenge.save()
    
    return JsonResponse({
        'success': True,
        'redirect': f'/problems/{challenge.problem.slug}/'
    })


@login_required
@require_http_methods(["POST"])
def complete_challenge(request):
    """Mark challenge as completed when user solves the problem."""
    challenge = DailyChallenge.objects.get_today_challenge()
    submission_id = request.POST.get('submission_id')
    
    if not submission_id:
        return JsonResponse({'error': 'Submission ID required'}, status=400)
    
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    
    # Check if submission is accepted
    if submission.status != 'accepted':
        return JsonResponse({'error': 'Submission not accepted'}, status=400)
    
    # Get or create participation
    participation, created = DailyChallengeParticipation.objects.get_or_create(
        user=request.user,
        challenge=challenge,
        defaults={'status': 'started'}
    )
    
    if participation.status == 'completed':
        return JsonResponse({'error': 'Challenge already completed'}, status=400)
    
    # Complete the challenge
    participation.complete(submission)
    
    # Get updated streak stats
    streak_stats = StreakStats.objects.get(user=request.user)
    
    return JsonResponse({
        'success': True,
        'coins_earned': participation.coins_earned,
        'xp_earned': participation.xp_earned,
        'current_streak': streak_stats.current_streak,
        'longest_streak': streak_stats.longest_streak,
    })


@login_required
def challenge_history(request):
    """Display user's challenge history."""
    participations = DailyChallengeParticipation.objects.filter(
        user=request.user
    ).select_related('challenge__problem').order_by('-started_at')[:30]
    
    streak_stats = StreakStats.objects.get_or_create(user=request.user)[0]
    
    context = {
        'participations': participations,
        'streak_stats': streak_stats,
    }
    return render(request, 'daily_challenges/challenge_history.html', context)


@login_required
def streak_leaderboard(request):
    """Display streak leaderboard."""
    top_streaks = StreakStats.objects.select_related('user').order_by('-current_streak')[:100]
    
    user_stats = StreakStats.objects.get_or_create(user=request.user)[0]
    
    context = {
        'top_streaks': top_streaks,
        'user_stats': user_stats,
    }
    return render(request, 'daily_challenges/streak_leaderboard.html', context)


@login_required
def streak_freeze_shop(request):
    """Display streak freeze items for purchase."""
    freeze_items = StreakFreezeItem.objects.filter(is_available=True)
    user_stats = StreakStats.objects.get_or_create(user=request.user)[0]
    
    context = {
        'freeze_items': freeze_items,
        'user_stats': user_stats,
        'user_coins': request.user.coins,
    }
    return render(request, 'daily_challenges/streak_freeze_shop.html', context)


@login_required
@require_http_methods(["POST"])
def purchase_streak_freeze(request):
    """Purchase a streak freeze item."""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    item = get_object_or_404(StreakFreezeItem, id=item_id, is_available=True)
    
    total_cost = item.cost_in_coins * quantity
    
    if request.user.coins < total_cost:
        return JsonResponse({'error': 'Insufficient coins'}, status=400)
    
    # Create purchase (will automatically deduct coins and add to user's freeze count)
    purchase = StreakFreezePurchase.objects.create(
        user=request.user,
        item=item,
        quantity=quantity,
        total_cost=total_cost
    )
    
    return JsonResponse({
        'success': True,
        'purchased': quantity,
        'total_cost': total_cost,
        'remaining_coins': request.user.coins,
    })


@login_required
@require_http_methods(["POST"])
def use_streak_freeze(request):
    """Use a streak freeze to protect streak."""
    user_stats = get_object_or_404(StreakStats, user=request.user)
    
    if not user_stats.can_use_freeze():
        return JsonResponse({'error': 'Cannot use streak freeze now'}, status=400)
    
    success = user_stats.use_streak_freeze()
    
    if success:
        return JsonResponse({
            'success': True,
            'remaining_freezes': user_stats.streak_freeze_count,
            'current_streak': user_stats.current_streak,
        })
    
    return JsonResponse({'error': 'Failed to use streak freeze'}, status=500)
