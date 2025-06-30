from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from users.models import User, CoinTransaction
from problems.models import Problem, Submission
from contests.models import Contest
from .models import SiteSettings, Notification

User = get_user_model()


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'college': user.college,
            'graduation_year': user.graduation_year,
            'coins': user.coins,
            'xp': user.xp,
            'level': user.level,
            'problems_solved': user.problems_solved,
            'contests_participated': user.contests_participated,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'preferred_language': user.preferred_language,
            'theme': user.theme,
            'date_joined': user.date_joined,
        }
        return Response(data)


class UserStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get submission statistics
        total_submissions = user.submissions.count()
        accepted_submissions = user.submissions.filter(status='accepted').count()
        acceptance_rate = (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        # Get problems solved by difficulty
        solved_problems = user.submissions.filter(status='accepted').values_list('problem__difficulty', flat=True)
        easy_solved = solved_problems.count('easy')
        medium_solved = solved_problems.count('medium')
        hard_solved = solved_problems.count('hard')
        
        # Get recent activity
        recent_submissions = user.submissions.order_by('-submitted_at')[:5]
        recent_transactions = user.coin_transactions.order_by('-timestamp')[:5]
        
        data = {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': round(acceptance_rate, 2),
            'difficulty_breakdown': {
                'easy': easy_solved,
                'medium': medium_solved,
                'hard': hard_solved,
            },
            'recent_submissions': [
                {
                    'id': sub.id,
                    'problem_title': sub.problem.title,
                    'status': sub.status,
                    'language': sub.language,
                    'submitted_at': sub.submitted_at,
                }
                for sub in recent_submissions
            ],
            'recent_transactions': [
                {
                    'id': trans.id,
                    'type': trans.transaction_type,
                    'amount': trans.amount,
                    'reason': trans.reason,
                    'timestamp': trans.timestamp,
                }
                for trans in recent_transactions
            ],
        }
        return Response(data)


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = request.user.notifications.order_by('-created_at')[:20]
        data = [
            {
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'is_read': notif.is_read,
                'related_url': notif.related_url,
                'created_at': notif.created_at,
            }
            for notif in notifications
        ]
        return Response(data)
    
    def post(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({'status': 'success'})
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SiteSettingsAPIView(APIView):
    def get(self, request):
        settings = SiteSettings.get_settings()
        data = {
            'site_name': settings.site_name,
            'site_description': settings.site_description,
            'enable_registration': settings.enable_registration,
            'enable_contests': settings.enable_contests,
            'enable_rewards': settings.enable_rewards,
            'maintenance_mode': settings.maintenance_mode,
            'maintenance_message': settings.maintenance_message,
        }
        return Response(data)


class LeaderboardAPIView(APIView):
    def get(self, request):
        # Get top users by different metrics
        top_by_solved = User.objects.annotate(
            solved_count=Count('submissions', filter={'submissions__status': 'accepted'})
        ).order_by('-solved_count', '-coins')[:10]
        
        top_by_coins = User.objects.order_by('-coins')[:10]
        top_by_xp = User.objects.order_by('-xp')[:10]
        top_by_streak = User.objects.order_by('-longest_streak')[:10]
        
        data = {
            'by_solved': [
                {
                    'username': user.username,
                    'solved_count': getattr(user, 'solved_count', 0),
                    'coins': user.coins,
                    'level': user.level,
                }
                for user in top_by_solved
            ],
            'by_coins': [
                {
                    'username': user.username,
                    'coins': user.coins,
                    'level': user.level,
                }
                for user in top_by_coins
            ],
            'by_xp': [
                {
                    'username': user.username,
                    'xp': user.xp,
                    'level': user.level,
                }
                for user in top_by_xp
            ],
            'by_streak': [
                {
                    'username': user.username,
                    'longest_streak': user.longest_streak,
                    'current_streak': user.current_streak,
                }
                for user in top_by_streak
            ],
        }
        return Response(data)


class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'results': []})
        
        # Search in problems
        problems = Problem.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status='published'
        )[:5]
        
        # Search in users
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )[:5]
        
        # Search in contests
        contests = Contest.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        
        data = {
            'problems': [
                {
                    'id': prob.id,
                    'title': prob.title,
                    'difficulty': prob.difficulty,
                    'acceptance_rate': prob.acceptance_rate,
                }
                for prob in problems
            ],
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'level': user.level,
                    'coins': user.coins,
                }
                for user in users
            ],
            'contests': [
                {
                    'id': contest.id,
                    'title': contest.title,
                    'contest_type': contest.contest_type,
                    'start_time': contest.start_time,
                }
                for contest in contests
            ],
        }
        return Response(data) 