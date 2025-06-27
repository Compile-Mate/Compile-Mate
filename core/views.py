from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from users.models import User, CoinTransaction
from problems.models import Problem, Submission, Tag
from contests.models import Contest
from rewards.models import Voucher
from .models import SiteSettings, FAQ

User = get_user_model()


def home(request):
    """Home page view."""
    # Get some basic stats
    total_problems = Problem.objects.filter(status='published').count()
    total_users = User.objects.count()
    total_submissions = Submission.objects.count()
    total_contests = Contest.objects.filter(status='ended').count()
    
    # Get recent problems
    recent_problems = Problem.objects.filter(status='published').order_by('-created_at')[:6]
    
    # Get upcoming contests
    upcoming_contests = Contest.objects.filter(
        status='upcoming',
        start_time__gt=timezone.now()
    ).order_by('start_time')[:3]
    
    # Get top users
    top_users = User.objects.annotate(
        solved_count=Count('submissions', filter=Q(submissions__status='accepted'))
    ).filter(solved_count__gt=0).order_by('-solved_count', '-xp')[:5]
    
    context = {
        'total_problems': total_problems,
        'total_users': total_users,
        'total_submissions': total_submissions,
        'total_contests': total_contests,
        'recent_problems': recent_problems,
        'upcoming_contests': upcoming_contests,
        'top_users': top_users,
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """User dashboard."""
    user = request.user
    
    # Get user's recent submissions
    recent_submissions = Submission.objects.filter(user=user).order_by('-submitted_at')[:5]
    
    # Get user's solved problems
    solved_problems = Problem.objects.filter(
        submissions__user=user,
        submissions__status='accepted'
    ).distinct()
    
    # Get user's upcoming contests
    user_contests = Contest.objects.filter(
        participants=user,
        status='upcoming'
    ).order_by('start_time')[:3]
    
    # Get user's achievements
    achievements = user.achievements.all()[:5]
    
    # Calculate level progress
    level_progress = int((user.xp % 1000) / 1000 * 100)
    
    context = {
        'user': user,
        'recent_submissions': recent_submissions,
        'solved_problems': solved_problems,
        'user_contests': user_contests,
        'achievements': achievements,
        'level_progress': level_progress,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    """User profile page."""
    user = request.user
    
    # Get user's statistics
    total_submissions = Submission.objects.filter(user=user).count()
    accepted_submissions = Submission.objects.filter(user=user, status='accepted').count()
    success_rate = (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0
    
    # Get user's recent activity
    recent_activity = user.activities.all()[:10]
    
    context = {
        'user': user,
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'success_rate': success_rate,
        'recent_activity': recent_activity,
    }
    return render(request, 'core/profile.html', context)


def leaderboard(request):
    """Global leaderboard: dynamic, not hardcoded."""
    # Order by problems solved, then XP, then coins
    users = User.objects.all().order_by('-problems_solved', '-xp', '-coins')
    top3 = list(users[:3])
    rest = users[3:50]  # Next 47 for the table
    # Find current user's rank if logged in
    user_rank = None
    if request.user.is_authenticated:
        user_list = list(users.values_list('id', flat=True))
        try:
            user_rank = user_list.index(request.user.id) + 1
        except ValueError:
            user_rank = None
    context = {
        'top3': top3,
        'rest': rest,
        'user_rank': user_rank,
    }
    return render(request, 'core/leaderboard.html', context)


def about(request):
    """About page."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page."""
    return render(request, 'core/contact.html')


def faq(request):
    """FAQ page."""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    return render(request, 'core/faq.html', {'faqs': faqs})


def privacy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy.html')


def terms(request):
    """Terms of service page."""
    return render(request, 'core/terms.html')


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get site settings
        settings = SiteSettings.get_settings()
        context['settings'] = settings
        
        # Get recent problems
        context['recent_problems'] = Problem.objects.filter(
            status='published'
        ).order_by('-created_at')[:6]
        
        # Get upcoming contests
        context['upcoming_contests'] = Contest.objects.filter(
            status='upcoming'
        ).order_by('start_time')[:3]
        
        # Get top users
        context['top_users'] = User.objects.annotate(
            solved_count=Count('submissions', filter={'submissions__status': 'accepted'})
        ).order_by('-solved_count', '-coins')[:10]
        
        # Get statistics
        context['total_users'] = User.objects.count()
        context['total_problems'] = Problem.objects.filter(status='published').count()
        context['total_submissions'] = Submission.objects.count()
        context['total_contests'] = Contest.objects.filter(status='ended').count()
        
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User statistics
        context['user'] = user
        context['problems_solved'] = user.problems_solved_count
        context['total_submissions'] = user.total_submissions_count
        context['acceptance_rate'] = user.acceptance_rate
        context['level_progress'] = int((user.xp % 1000) / 1000 * 100)
        
        # Recent activity
        context['recent_submissions'] = user.submissions.order_by('-submitted_at')[:5]
        context['recent_contests'] = user.contests.order_by('-start_time')[:3]
        
        # Coin transactions
        context['recent_transactions'] = user.coin_transactions.order_by('-timestamp')[:5]
        
        # Streak information
        context['current_streak'] = user.dynamic_streak
        context['longest_streak'] = user.longest_streak_dynamic
        
        # Recommended problems
        solved_problems = set(user.submissions.filter(status='accepted').values_list('problem_id', flat=True))
        context['recommended_problems'] = Problem.objects.filter(
            status='published'
        ).exclude(id__in=solved_problems).order_by('?')[:3]
        
        # Upcoming contests
        context['upcoming_contests'] = Contest.objects.filter(
            status='upcoming'
        ).order_by('start_time')[:3]
        
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'core/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        # Allow users to view their own profile or other public profiles
        username = self.kwargs.get('username')
        if username:
            return User.objects.get(username=username)
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['profile_user']
        
        # User statistics
        context['problems_solved'] = user.submissions.filter(status='accepted').count()
        context['total_submissions'] = user.submissions.count()
        context['acceptance_rate'] = (
            (context['problems_solved'] / context['total_submissions'] * 100)
            if context['total_submissions'] > 0 else 0
        )
        
        # Recent submissions
        context['recent_submissions'] = user.submissions.order_by('-submitted_at')[:10]
        
        # Solved problems by difficulty
        solved_problems = user.submissions.filter(status='accepted').values_list('problem__difficulty', flat=True)
        context['easy_solved'] = solved_problems.count('easy')
        context['medium_solved'] = solved_problems.count('medium')
        context['hard_solved'] = solved_problems.count('hard')
        
        # Contest history
        context['contest_history'] = user.contests.filter(status='ended').order_by('-start_time')[:5]
        
        # Achievements
        context['achievements'] = user.achievements.order_by('-earned_at')
        
        return context


class LeaderboardView(ListView):
    model = User
    template_name = 'core/leaderboard.html'
    context_object_name = 'users'
    paginate_by = 50
    
    def get_queryset(self):
        return User.objects.annotate(
            solved_count=Count('submissions', filter={'submissions__status': 'accepted'})
        ).order_by('-solved_count', '-coins', '-xp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top users by different metrics
        context['top_by_coins'] = User.objects.order_by('-coins')[:10]
        context['top_by_xp'] = User.objects.order_by('-xp')[:10]
        context['top_by_streak'] = User.objects.order_by('-longest_streak')[:10]
        
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class FAQView(TemplateView):
    template_name = 'core/faq.html'


class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    template_name = 'core/terms.html' 