"""
Views for Real-Time Code Battles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import Battle, BattleInvitation, BattleStats
from problems.models import Problem
from users.models import User


@login_required
def battle_list(request):
    """Display list of active and available battles."""
    active_battles = Battle.objects.filter(
        status='in_progress'
    ).select_related('challenger', 'opponent', 'problem')
    
    waiting_battles = Battle.objects.filter(
        status='waiting',
        mode='random'
    ).select_related('challenger', 'problem')
    
    user_battles = Battle.objects.filter(
        Q(challenger=request.user) | Q(opponent=request.user)
    ).select_related('challenger', 'opponent', 'problem').order_by('-created_at')[:10]
    
    # Get user battle stats
    battle_stats, _ = BattleStats.objects.get_or_create(user=request.user)
    
    # Get pending invitations
    pending_invitations = BattleInvitation.objects.filter(
        to_user=request.user,
        status='pending',
        expires_at__gt=timezone.now()
    ).select_related('from_user', 'problem')
    
    context = {
        'active_battles': active_battles,
        'waiting_battles': waiting_battles,
        'user_battles': user_battles,
        'battle_stats': battle_stats,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'battles/battle_list.html', context)


@login_required
def create_battle(request):
    """Create a new battle."""
    if request.method == 'POST':
        problem_id = request.POST.get('problem_id')
        stake = int(request.POST.get('stake', 50))
        mode = request.POST.get('mode', 'random')
        opponent_username = request.POST.get('opponent_username', '')
        
        # Validate stake
        if stake > request.user.coins:
            return JsonResponse({'error': 'Insufficient coins'}, status=400)
        
        # Get problem
        problem = get_object_or_404(Problem, id=problem_id)
        
        if mode == 'friend' and opponent_username:
            # Create friend invitation
            opponent = get_object_or_404(User, username=opponent_username)
            
            if opponent == request.user:
                return JsonResponse({'error': 'Cannot challenge yourself'}, status=400)
            
            invitation = BattleInvitation.objects.create(
                from_user=request.user,
                to_user=opponent,
                problem=problem,
                stake=stake,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            return JsonResponse({
                'success': True,
                'invitation_id': invitation.id,
                'message': 'Invitation sent!'
            })
        else:
            # Create random battle
            battle = Battle.objects.create(
                mode='random',
                challenger=request.user,
                problem=problem,
                stake=stake
            )
            
            # Deduct stake from user
            request.user.coins -= stake
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'battle_id': str(battle.battle_id),
                'redirect': f'/battles/{battle.battle_id}/'
            })
    
    # GET request - show create form
    problems = Problem.objects.filter(status='published').order_by('-created_at')[:50]
    context = {'problems': problems}
    return render(request, 'battles/create_battle.html', context)


@login_required
def battle_arena(request, battle_id):
    """Battle arena page."""
    battle = get_object_or_404(Battle, battle_id=battle_id)
    
    # Check if user is authorized
    is_participant = request.user == battle.challenger or request.user == battle.opponent
    is_spectator = battle.spectators.filter(id=request.user.id).exists()
    
    if not (is_participant or is_spectator or request.user.is_staff):
        # Add as spectator
        battle.spectators.add(request.user)
        battle.spectator_count += 1
        battle.save()
    
    context = {
        'battle': battle,
        'is_participant': is_participant,
        'is_spectator': not is_participant,
    }
    return render(request, 'battles/battle_arena.html', context)


@login_required
@require_http_methods(["POST"])
def join_battle(request, battle_id):
    """Join an open battle."""
    battle = get_object_or_404(Battle, battle_id=battle_id)
    
    if battle.status != 'waiting':
        return JsonResponse({'error': 'Battle is not available'}, status=400)
    
    if battle.challenger == request.user:
        return JsonResponse({'error': 'Cannot join your own battle'}, status=400)
    
    if request.user.coins < battle.stake:
        return JsonResponse({'error': 'Insufficient coins'}, status=400)
    
    # Join battle
    battle.opponent = request.user
    battle.start_battle()
    
    # Deduct stake from user
    request.user.coins -= battle.stake
    request.user.save()
    
    return JsonResponse({
        'success': True,
        'battle_id': str(battle.battle_id),
        'redirect': f'/battles/{battle.battle_id}/'
    })


@login_required
@require_http_methods(["POST"])
def accept_invitation(request, invitation_id):
    """Accept a battle invitation."""
    invitation = get_object_or_404(BattleInvitation, id=invitation_id, to_user=request.user)
    
    if invitation.status != 'pending':
        return JsonResponse({'error': 'Invitation is no longer valid'}, status=400)
    
    if timezone.now() > invitation.expires_at:
        invitation.status = 'expired'
        invitation.save()
        return JsonResponse({'error': 'Invitation has expired'}, status=400)
    
    if request.user.coins < invitation.stake:
        return JsonResponse({'error': 'Insufficient coins'}, status=400)
    
    # Accept invitation and create battle
    battle = invitation.accept()
    
    if battle:
        # Deduct stakes from both users
        request.user.coins -= battle.stake
        request.user.save()
        
        invitation.from_user.coins -= battle.stake
        invitation.from_user.save()
        
        # Start battle
        battle.start_battle()
        
        return JsonResponse({
            'success': True,
            'battle_id': str(battle.battle_id),
            'redirect': f'/battles/{battle.battle_id}/'
        })
    
    return JsonResponse({'error': 'Failed to create battle'}, status=500)


@login_required
@require_http_methods(["POST"])
def decline_invitation(request, invitation_id):
    """Decline a battle invitation."""
    invitation = get_object_or_404(BattleInvitation, id=invitation_id, to_user=request.user)
    
    if invitation.status == 'pending':
        invitation.decline()
        return JsonResponse({'success': True, 'message': 'Invitation declined'})
    
    return JsonResponse({'error': 'Invitation is no longer valid'}, status=400)


@login_required
def battle_history(request):
    """Display user's battle history."""
    battles = Battle.objects.filter(
        Q(challenger=request.user) | Q(opponent=request.user),
        status='completed'
    ).select_related('challenger', 'opponent', 'problem', 'winner').order_by('-ended_at')
    
    battle_stats, _ = BattleStats.objects.get_or_create(user=request.user)
    
    context = {
        'battles': battles,
        'battle_stats': battle_stats,
    }
    return render(request, 'battles/battle_history.html', context)


@login_required
def leaderboard(request):
    """Display battle leaderboard."""
    top_battlers = BattleStats.objects.select_related('user').order_by('-battles_won')[:100]
    
    user_stats, _ = BattleStats.objects.get_or_create(user=request.user)
    
    context = {
        'top_battlers': top_battlers,
        'user_stats': user_stats,
    }
    return render(request, 'battles/leaderboard.html', context)
