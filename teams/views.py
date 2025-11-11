"""
Views for Teams & Clan System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .models import Team, TeamMembership, TeamInvitation, TeamContest, TeamAchievement
from users.models import User


@login_required
def team_list(request):
    """Display all teams."""
    teams = Team.objects.annotate(
        member_count=Count('members'),
        total_points=Sum('members__xp')
    ).order_by('-total_points')
    
    # Get user's team
    user_team = None
    try:
        membership = TeamMembership.objects.get(user=request.user)
        user_team = membership.team
    except TeamMembership.DoesNotExist:
        pass
    
    # Get pending invitations
    pending_invitations = TeamInvitation.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('team')
    
    context = {
        'teams': teams,
        'user_team': user_team,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'teams/team_list.html', context)


@login_required
def team_detail(request, team_id):
    """Display team details."""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is member
    is_member = TeamMembership.objects.filter(team=team, user=request.user).exists()
    
    # Get team members
    members = TeamMembership.objects.filter(team=team).select_related('user').order_by('-role', '-joined_at')
    
    # Get team achievements
    achievements = TeamAchievement.objects.filter(team=team).order_by('-earned_at')[:10]
    
    # Get team contests
    contests = TeamContest.objects.filter(team=team).select_related('contest').order_by('-participation_date')[:10]
    
    context = {
        'team': team,
        'is_member': is_member,
        'members': members,
        'achievements': achievements,
        'contests': contests,
    }
    return render(request, 'teams/team_detail.html', context)


@login_required
def create_team(request):
    """Create a new team."""
    if request.method == 'POST':
        from django.utils.text import slugify
        
        name = request.POST.get('name')
        description = request.POST.get('description')
        slug = slugify(name)
        is_public = request.POST.get('is_public') == 'on'
        
        # Check if user already in a team
        if TeamMembership.objects.filter(user=request.user).exists():
            return JsonResponse({'error': 'Already in a team'}, status=400)
        
        # Create team
        team = Team.objects.create(
            name=name,
            slug=slug,
            description=description,
            founder=request.user,
            is_public=is_public
        )
        
        # Add creator as founder
        TeamMembership.objects.create(
            team=team,
            user=request.user,
            role='founder'
        )
        
        return redirect('teams:team_detail', team_id=team.id)
    
    return render(request, 'teams/create_team.html')


@login_required
@require_http_methods(["POST"])
def join_team(request, team_id):
    """Join a public team."""
    team = get_object_or_404(Team, id=team_id)
    
    if not team.is_public:
        return JsonResponse({'error': 'Team is private'}, status=400)
    
    if TeamMembership.objects.filter(user=request.user).exists():
        return JsonResponse({'error': 'Already in a team'}, status=400)
    
    # Join team
    TeamMembership.objects.create(
        team=team,
        user=request.user,
        role='member'
    )
    
    return JsonResponse({'success': True, 'redirect': f'/teams/{team.id}/'})


@login_required
@require_http_methods(["POST"])
def leave_team(request, team_id):
    """Leave a team."""
    team = get_object_or_404(Team, id=team_id)
    membership = get_object_or_404(TeamMembership, team=team, user=request.user)
    
    if membership.role == 'founder':
        # Transfer leadership or disband
        other_members = TeamMembership.objects.filter(team=team).exclude(user=request.user)
        if other_members.exists():
            new_leader = other_members.first()
            new_leader.role = 'founder'
            new_leader.save()
            team.founder = new_leader.user
            team.save()
        else:
            # Last member, delete team
            team.delete()
            return JsonResponse({'success': True, 'redirect': '/teams/'})
    
    membership.delete()
    return JsonResponse({'success': True, 'redirect': '/teams/'})


@login_required
@require_http_methods(["POST"])
def invite_member(request, team_id):
    """Invite a user to team."""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is founder or leader
    membership = TeamMembership.objects.filter(team=team, user=request.user).first()
    if not membership or membership.role not in ['founder', 'leader']:
        return JsonResponse({'error': 'No permission'}, status=403)
    
    username = request.POST.get('username')
    to_user = get_object_or_404(User, username=username)
    
    if TeamMembership.objects.filter(user=to_user).exists():
        return JsonResponse({'error': 'User already in a team'}, status=400)
    
    # Create invitation
    invitation = TeamInvitation.objects.create(
        team=team,
        from_user=request.user,
        to_user=to_user
    )
    
    return JsonResponse({'success': True, 'invitation_id': invitation.id})


@login_required
@require_http_methods(["POST"])
def accept_invitation(request, invitation_id):
    """Accept team invitation."""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, to_user=request.user)
    
    if invitation.status != 'pending':
        return JsonResponse({'error': 'Invitation not valid'}, status=400)
    
    if TeamMembership.objects.filter(user=request.user).exists():
        return JsonResponse({'error': 'Already in a team'}, status=400)
    
    # Accept invitation
    invitation.accept()
    
    return JsonResponse({'success': True, 'redirect': f'/teams/{invitation.team.id}/'})


@login_required
@require_http_methods(["POST"])
def decline_invitation(request, invitation_id):
    """Decline team invitation."""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, to_user=request.user)
    
    if invitation.status == 'pending':
        invitation.decline()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invitation not valid'}, status=400)
