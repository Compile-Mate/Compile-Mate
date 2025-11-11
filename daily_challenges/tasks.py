"""
Celery Tasks for Daily Challenges
Handles automated daily challenge selection, streak management, and notifications
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


@shared_task
def select_daily_challenge():
    """
    Select and create today's daily challenge.
    Runs every day at midnight.
    """
    from daily_challenges.models import DailyChallenge
    from problems.models import Problem
    import random
    
    today = timezone.now().date()
    
    # Check if today's challenge already exists
    if DailyChallenge.objects.filter(date=today).exists():
        return f"Daily challenge for {today} already exists"
    
    # Get recent challenges (last 30 days) to avoid repetition
    recent_challenges = DailyChallenge.objects.filter(
        date__gte=today - timedelta(days=30)
    ).values_list('problem_id', flat=True)
    
    # Select a medium difficulty problem that hasn't been used recently
    available_problems = Problem.objects.filter(
        status='published',
        difficulty='medium'
    ).exclude(id__in=recent_challenges)
    
    if not available_problems.exists():
        # If no medium problems available, try easy
        available_problems = Problem.objects.filter(
            status='published',
            difficulty='easy'
        ).exclude(id__in=recent_challenges)
    
    if not available_problems.exists():
        # Last resort: any published problem
        available_problems = Problem.objects.filter(status='published')
    
    if available_problems.exists():
        selected_problem = random.choice(available_problems)
        
        # Create daily challenge
        challenge = DailyChallenge.objects.create(
            date=today,
            problem=selected_problem,
            bonus_coins=50,
            bonus_xp=100
        )
        
        # Notify users
        notify_users_of_daily_challenge.delay(challenge.id)
        
        return f"Created daily challenge for {today}: {selected_problem.title}"
    
    return "No available problems for daily challenge"


@shared_task
def notify_users_of_daily_challenge(challenge_id):
    """
    Notify active users about the new daily challenge.
    """
    from daily_challenges.models import DailyChallenge
    from users.models import User
    from core.models import Notification
    
    try:
        challenge = DailyChallenge.objects.select_related('problem').get(id=challenge_id)
        
        # Get active users (logged in within last 7 days)
        active_users = User.objects.filter(
            last_activity__gte=timezone.now() - timedelta(days=7)
        )
        
        # Create notifications in bulk
        notifications = [
            Notification(
                user=user,
                title="🎯 New Daily Challenge!",
                message=f"Today's challenge: {challenge.problem.title}. Complete it to earn bonus coins and maintain your streak!",
                notification_type='daily_challenge',
                link=f"/problems/{challenge.problem.slug}/"
            )
            for user in active_users
        ]
        
        Notification.objects.bulk_create(notifications, batch_size=1000)
        
        return f"Notified {len(notifications)} users about daily challenge"
        
    except DailyChallenge.DoesNotExist:
        return f"Daily challenge {challenge_id} not found"


@shared_task
def check_expired_streaks():
    """
    Check for expired streaks and notify users.
    Runs every hour.
    """
    from daily_challenges.models import StreakStats
    from core.models import Notification
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Find users whose streak is about to break (last completed yesterday)
    at_risk_users = StreakStats.objects.filter(
        last_completed_date=yesterday,
        current_streak__gt=0
    ).select_related('user')
    
    notifications_created = 0
    
    for streak_stat in at_risk_users:
        # Check if they can use a streak freeze
        if streak_stat.can_use_freeze():
            Notification.objects.create(
                user=streak_stat.user,
                title="⚠️ Streak at Risk!",
                message=f"Your {streak_stat.current_streak} day streak is at risk! Use a Streak Freeze or complete today's challenge.",
                notification_type='streak_warning',
                link="/daily-challenge/"
            )
            notifications_created += 1
    
    return f"Sent {notifications_created} streak warning notifications"


@shared_task
def update_streak_leaderboard():
    """
    Update daily challenge leaderboard for completed challenges.
    Runs every 10 minutes.
    """
    from daily_challenges.models import DailyChallenge, DailyChallengeLeaderboard, DailyChallengeParticipation
    
    today = timezone.now().date()
    
    try:
        challenge = DailyChallenge.objects.get(date=today)
        
        # Get all completed participations for today, ordered by time
        completed_participations = DailyChallengeParticipation.objects.filter(
            challenge=challenge,
            status='completed'
        ).select_related('user').order_by('time_taken')
        
        # Clear existing leaderboard
        DailyChallengeLeaderboard.objects.filter(challenge=challenge).delete()
        
        # Create new leaderboard entries
        leaderboard_entries = []
        for rank, participation in enumerate(completed_participations, start=1):
            leaderboard_entries.append(
                DailyChallengeLeaderboard(
                    challenge=challenge,
                    user=participation.user,
                    rank=rank,
                    time_taken=participation.time_taken,
                    completed_at=participation.completed_at
                )
            )
        
        DailyChallengeLeaderboard.objects.bulk_create(leaderboard_entries)
        
        return f"Updated leaderboard for {today}: {len(leaderboard_entries)} entries"
        
    except DailyChallenge.DoesNotExist:
        return f"No daily challenge found for {today}"


@shared_task
def award_streak_milestones():
    """
    Award badges and rewards for streak milestones.
    Runs daily at 11:59 PM.
    """
    from daily_challenges.models import StreakStats
    from achievements.models import Badge, UserBadge
    from users.models import User
    from core.models import Notification
    
    # Milestone thresholds
    milestones = {
        7: {'coins': 100, 'xp': 200, 'badge_name': '7 Day Streak'},
        30: {'coins': 500, 'xp': 1000, 'badge_name': '30 Day Streak'},
        50: {'coins': 1000, 'xp': 2500, 'badge_name': '50 Day Streak'},
        100: {'coins': 5000, 'xp': 10000, 'badge_name': '100 Day Streak'},
        365: {'coins': 25000, 'xp': 50000, 'badge_name': '1 Year Streak'},
    }
    
    awarded_count = 0
    
    for milestone, rewards in milestones.items():
        # Find users who just hit this milestone
        users_at_milestone = StreakStats.objects.filter(
            current_streak=milestone
        ).select_related('user')
        
        for streak_stat in users_at_milestone:
            user = streak_stat.user
            
            # Award coins and XP
            user.coins += rewards['coins']
            user.xp += rewards['xp']
            user.save()
            
            # Try to award badge if it exists
            try:
                badge = Badge.objects.get(name=rewards['badge_name'], badge_type='streak')
                UserBadge.objects.get_or_create(user=user, badge=badge)
            except Badge.DoesNotExist:
                pass
            
            # Create celebration notification
            Notification.objects.create(
                user=user,
                title=f"🔥 {milestone} Day Streak Milestone!",
                message=f"Incredible! You've maintained a {milestone} day streak. Earned {rewards['coins']} coins and {rewards['xp']} XP!",
                notification_type='achievement',
                link="/dashboard/"
            )
            
            awarded_count += 1
    
    return f"Awarded {awarded_count} streak milestone rewards"


@shared_task
def cleanup_old_challenges():
    """
    Archive old daily challenges and cleanup data.
    Runs weekly.
    """
    from daily_challenges.models import DailyChallenge, DailyChallengeParticipation
    
    # Delete challenges older than 90 days
    cutoff_date = timezone.now().date() - timedelta(days=90)
    
    old_challenges = DailyChallenge.objects.filter(date__lt=cutoff_date)
    count = old_challenges.count()
    
    # Delete associated participations
    DailyChallengeParticipation.objects.filter(challenge__in=old_challenges).delete()
    
    # Delete challenges
    old_challenges.delete()
    
    return f"Cleaned up {count} old daily challenges"


@shared_task
def send_streak_freeze_reminder():
    """
    Remind users with expiring streak freezes.
    Runs daily.
    """
    from daily_challenges.models import StreakStats
    from core.models import Notification
    
    # Find users with low streak freeze count
    low_freeze_users = StreakStats.objects.filter(
        current_streak__gte=7,
        streak_freeze_count__lte=1
    ).select_related('user')
    
    notifications_created = 0
    
    for streak_stat in low_freeze_users:
        Notification.objects.create(
            user=streak_stat.user,
            title="💡 Streak Freeze Low!",
            message=f"You have {streak_stat.streak_freeze_count} streak freeze(s) left. Consider purchasing more to protect your {streak_stat.current_streak} day streak!",
            notification_type='reminder',
            link="/marketplace/"
        )
        notifications_created += 1
    
    return f"Sent {notifications_created} streak freeze reminders"

