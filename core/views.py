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
from django.views import View
from django.utils.decorators import method_decorator
import json

from users.models import User, CoinTransaction
from problems.models import Problem, Submission, Tag
from contests.models import Contest
from rewards.models import Voucher
from .models import SiteSettings, FAQ, SupportChat, ChatMessage, AdminAvailability, ChatTemplate, ChatRating

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
        solved_problems = list(user.submissions.filter(status='accepted').values_list('problem__difficulty', flat=True))
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


@login_required
def support_chat_list(request):
    """Display user's support chat history."""
    chats = SupportChat.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        chats = chats.filter(status=status)
    
    context = {
        'chats': chats,
        'status_filter': status,
    }
    return render(request, 'core/support_chat_list.html', context)


@login_required
def support_chat_detail(request, chat_id):
    """Display individual support chat."""
    chat = get_object_or_404(SupportChat, id=chat_id, user=request.user)
    messages = chat.messages.all()
    
    # Mark messages as read
    unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True, read_at=timezone.now())
    
    context = {
        'chat': chat,
        'messages': messages,
    }
    return render(request, 'core/support_chat_detail.html', context)


@login_required
def create_support_chat(request):
    """Create a new support chat."""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        category = request.POST.get('category', 'general')
        priority = request.POST.get('priority', 'medium')
        
        if subject and description:
            chat = SupportChat.objects.create(
                user=request.user,
                subject=subject,
                description=description,
                category=category,
                priority=priority,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                page_url=request.META.get('HTTP_REFERER', ''),
            )
            
            # Create initial system message
            ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                content=f"Chat created: {description}",
                message_type='system'
            )
            
            messages.success(request, 'Support chat created successfully!')
            return redirect('core:support_chat_detail', chat_id=chat.id)
    
    context = {
        'categories': SupportChat._meta.get_field('category').choices,
        'priorities': SupportChat._meta.get_field('priority').choices,
    }
    return render(request, 'core/create_support_chat.html', context)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ChatMessageAPIView(View):
    """API view for sending and receiving chat messages."""
    
    def post(self, request, chat_id):
        """Send a new message."""
        try:
            chat = SupportChat.objects.get(id=chat_id, user=request.user)
            data = json.loads(request.body)
            
            message_type = data.get('message_type', 'text')
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'error': 'Message content is required'}, status=400)
            
            # Create message
            message = ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                content=content,
                message_type=message_type,
                metadata=data.get('metadata', {})
            )
            
            # Update chat last activity
            chat.last_activity = timezone.now()
            chat.save()
            
            # Auto-assign admin if available
            if not chat.admin and chat.status == 'open':
                available_admin = AdminAvailability.objects.filter(
                    is_online=True,
                    is_available=True,
                    current_chats__lt=F('max_concurrent_chats')
                ).first()
                
                if available_admin:
                    chat.admin = available_admin.admin
                    chat.status = 'in_progress'
                    chat.save()
                    
                    # Update admin workload
                    available_admin.current_chats += 1
                    available_admin.save()
                    
                    # Notify admin (you can implement WebSocket notification here)
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'message_type': message.message_type,
                    'sender': message.sender.username,
                    'created_at': message.created_at.isoformat(),
                }
            })
            
        except SupportChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request, chat_id):
        """Get chat messages."""
        try:
            chat = SupportChat.objects.get(id=chat_id, user=request.user)
            last_message_id = request.GET.get('last_message_id', 0)
            
            # Get new messages
            messages = chat.messages.filter(id__gt=last_message_id)
            
            # Mark messages as read
            unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
            unread_messages.update(is_read=True, read_at=timezone.now())
            
            return JsonResponse({
                'messages': [
                    {
                        'id': msg.id,
                        'content': msg.content,
                        'message_type': msg.message_type,
                        'sender': msg.sender.username,
                        'created_at': msg.created_at.isoformat(),
                        'is_read': msg.is_read,
                    }
                    for msg in messages
                ]
            })
            
        except SupportChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)


@login_required
def chat_templates(request):
    """Get chat response templates for admins."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    category = request.GET.get('category', '')
    templates = ChatTemplate.objects.filter(is_active=True)
    
    if category:
        templates = templates.filter(category=category)
    
    return JsonResponse({
        'templates': [
            {
                'id': template.id,
                'name': template.name,
                'content': template.content,
                'category': template.category,
            }
            for template in templates
        ]
    })


@login_required
def rate_chat(request, chat_id):
    """Rate a completed chat session."""
    chat = get_object_or_404(SupportChat, id=chat_id, user=request.user)
    
    if chat.status not in ['resolved', 'closed']:
        messages.error(request, 'Can only rate completed chats.')
        return redirect('core:support_chat_detail', chat_id=chat.id)
    
    if hasattr(chat, 'rating'):
        messages.warning(request, 'You have already rated this chat.')
        return redirect('core:support_chat_detail', chat_id=chat.id)
    
    if request.method == 'POST':
        overall_rating = request.POST.get('overall_rating')
        response_time_rating = request.POST.get('response_time_rating')
        helpfulness_rating = request.POST.get('helpfulness_rating')
        feedback = request.POST.get('feedback', '')
        suggestions = request.POST.get('suggestions', '')
        
        if overall_rating and response_time_rating and helpfulness_rating:
            rating = ChatRating.objects.create(
                chat=chat,
                user=request.user,
                overall_rating=int(overall_rating),
                response_time_rating=int(response_time_rating),
                helpfulness_rating=int(helpfulness_rating),
                feedback=feedback,
                suggestions=suggestions,
            )
            
            # Update admin metrics if admin exists
            if chat.admin:
                admin_availability = AdminAvailability.objects.get(admin=chat.admin)
                admin_availability.chats_resolved += 1
                admin_availability.satisfaction_rating = (
                    (admin_availability.satisfaction_rating * (admin_availability.chats_resolved - 1) + 
                     int(overall_rating)) / admin_availability.chats_resolved
                )
                admin_availability.save()
            
            messages.success(request, 'Thank you for your feedback!')
            return redirect('core:support_chat_detail', chat_id=chat.id)
    
    return render(request, 'core/rate_chat.html', {'chat': chat})


# Admin Views for Support Management
@login_required
def admin_chat_dashboard(request):
    """Admin dashboard for managing support chats."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get chat statistics
    total_chats = SupportChat.objects.count()
    open_chats = SupportChat.objects.filter(status__in=['open', 'waiting']).count()
    in_progress_chats = SupportChat.objects.filter(status='in_progress').count()
    resolved_today = SupportChat.objects.filter(
        status='resolved',
        resolved_at__date=timezone.now().date()
    ).count()
    
    # Get recent chats
    recent_chats = SupportChat.objects.filter(
        status__in=['open', 'waiting', 'in_progress']
    ).order_by('-created_at')[:10]
    
    # Get admin availability
    admin_availability = AdminAvailability.objects.filter(admin=request.user).first()
    
    context = {
        'total_chats': total_chats,
        'open_chats': open_chats,
        'in_progress_chats': in_progress_chats,
        'resolved_today': resolved_today,
        'recent_chats': recent_chats,
        'admin_availability': admin_availability,
    }
    return render(request, 'core/admin_chat_dashboard.html', context)


@login_required
def admin_chat_list(request):
    """Admin view of all support chats."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    chats = SupportChat.objects.all().order_by('-created_at')
    
    # Filtering
    status = request.GET.get('status')
    if status:
        chats = chats.filter(status=status)
    
    priority = request.GET.get('priority')
    if priority:
        chats = chats.filter(priority=priority)
    
    category = request.GET.get('category')
    if category:
        chats = chats.filter(category=category)
    
    # Pagination
    paginator = Paginator(chats, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'priority_filter': priority,
        'category_filter': category,
    }
    return render(request, 'core/admin_chat_list.html', context)


@login_required
def admin_chat_detail(request, chat_id):
    """Admin view of individual chat."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    chat = get_object_or_404(SupportChat, id=chat_id)
    messages = chat.messages.all()
    
    # Mark messages as read
    unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True, read_at=timezone.now())
    
    # Get response templates
    templates = ChatTemplate.objects.filter(is_active=True, category=chat.category)
    
    context = {
        'chat': chat,
        'messages': messages,
        'templates': templates,
    }
    return render(request, 'core/admin_chat_detail.html', context)


@login_required
def admin_assign_chat(request, chat_id):
    """Assign chat to admin."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        chat = SupportChat.objects.get(id=chat_id, status__in=['open', 'waiting'])
        chat.admin = request.user
        chat.status = 'in_progress'
        chat.save()
        
        # Update admin workload
        admin_availability, created = AdminAvailability.objects.get_or_create(
            admin=request.user,
            defaults={'current_chats': 1}
        )
        if not created:
            admin_availability.current_chats += 1
            admin_availability.save()
        
        return JsonResponse({'success': True})
    except SupportChat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found or not available'}, status=404)


@login_required
def admin_resolve_chat(request, chat_id):
    """Mark chat as resolved."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        chat = SupportChat.objects.get(id=chat_id, admin=request.user)
        chat.status = 'resolved'
        chat.resolved_at = timezone.now()
        chat.save()
        
        # Update admin workload
        admin_availability = AdminAvailability.objects.get(admin=request.user)
        admin_availability.current_chats = max(0, admin_availability.current_chats - 1)
        admin_availability.save()
        
        return JsonResponse({'success': True})
    except SupportChat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404) 