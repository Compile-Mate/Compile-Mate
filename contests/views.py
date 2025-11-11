from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse

from .models import Contest, ContestParticipation, ContestLeaderboard
from problems.models import Problem


def contest_list(request):
    """Display list of all contests."""
    contests = Contest.objects.all().order_by('-start_time')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        contests = contests.filter(status=status)
    
    # Pagination
    paginator = Paginator(contests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'contests/contest_list.html', context)


def contest_detail(request, slug):
    """Display contest details."""
    contest = get_object_or_404(Contest, slug=slug)
    
    # Check if user is participating
    is_participating = False
    participation = None
    if request.user.is_authenticated:
        participation = ContestParticipation.objects.filter(
            contest=contest, 
            user=request.user
        ).first()
        is_participating = participation is not None
    
    # Get leaderboard
    leaderboard = ContestLeaderboard.objects.filter(
        contest=contest
    ).order_by('rank')[:20]
    
    context = {
        'contest': contest,
        'is_participating': is_participating,
        'participation': participation,
        'leaderboard': leaderboard,
    }
    return render(request, 'contests/contest_detail.html', context)


@login_required
def contest_register(request, slug):
    """Register for a contest."""
    contest = get_object_or_404(Contest, slug=slug)
    
    if not contest.allow_registration:
        messages.error(request, 'Registration is not allowed for this contest.')
        return redirect('contests:contest_detail', slug=slug)
    
    if contest.is_ended:
        messages.error(request, 'This contest has already ended.')
        return redirect('contests:contest_detail', slug=slug)
    
    # Check if already registered
    if ContestParticipation.objects.filter(contest=contest, user=request.user).exists():
        messages.warning(request, 'You are already registered for this contest.')
        return redirect('contests:contest_detail', slug=slug)
    
    # Check max participants
    if contest.max_participants and contest.participants.count() >= contest.max_participants:
        messages.error(request, 'This contest is full.')
        return redirect('contests:contest_detail', slug=slug)
    
    # Register user
    participation = ContestParticipation.objects.create(
        contest=contest,
        user=request.user
    )
    
    messages.success(request, f'Successfully registered for {contest.title}!')
    return redirect('contests:contest_detail', slug=slug)


@login_required
def contest_problems(request, slug):
    """Display contest problems."""
    contest = get_object_or_404(Contest, slug=slug)
    participation = get_object_or_404(
        ContestParticipation, 
        contest=contest, 
        user=request.user
    )
    
    # Get contest problems with ordering
    contest_problems = contest.contestproblem_set.filter(
        is_visible=True
    ).order_by('order')
    
    context = {
        'contest': contest,
        'participation': participation,
        'contest_problems': contest_problems,
    }
    return render(request, 'contests/contest_problems.html', context)


@login_required
def contest_leaderboard(request, slug):
    """Display contest leaderboard."""
    contest = get_object_or_404(Contest, slug=slug)
    
    leaderboard = ContestLeaderboard.objects.filter(
        contest=contest
    ).order_by('rank')
    
    context = {
        'contest': contest,
        'leaderboard': leaderboard,
    }
    return render(request, 'contests/contest_leaderboard.html', context)


@login_required
def contest_submissions(request, slug):
    """Display user's contest submissions."""
    contest = get_object_or_404(Contest, slug=slug)
    participation = get_object_or_404(
        ContestParticipation, 
        contest=contest, 
        user=request.user
    )
    
    submissions = participation.contestsubmission_set.all().order_by('-submitted_at')
    
    context = {
        'contest': contest,
        'participation': participation,
        'submissions': submissions,
    }
    return render(request, 'contests/contest_submissions.html', context) 