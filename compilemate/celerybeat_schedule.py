"""
Celery Beat Schedule Configuration
Defines all periodic tasks for CompileMate
"""

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # Daily Challenge Selection - Every day at midnight
    'select-daily-challenge': {
        'task': 'daily_challenges.tasks.select_daily_challenge',
        'schedule': crontab(hour=0, minute=0),
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not executed
        }
    },
    
    # Check Expired Streaks - Every hour
    'check-expired-streaks': {
        'task': 'daily_challenges.tasks.check_expired_streaks',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Update Streak Leaderboard - Every 10 minutes
    'update-streak-leaderboard': {
        'task': 'daily_challenges.tasks.update_streak_leaderboard',
        'schedule': crontab(minute='*/10'),
    },
    
    # Award Streak Milestones - Every day at 11:59 PM
    'award-streak-milestones': {
        'task': 'daily_challenges.tasks.award_streak_milestones',
        'schedule': crontab(hour=23, minute=59),
    },
    
    # Cleanup Old Challenges - Every Sunday at 2 AM
    'cleanup-old-challenges': {
        'task': 'daily_challenges.tasks.cleanup_old_challenges',
        'schedule': crontab(hour=2, minute=0, day_of_week='sunday'),
    },
    
    # Send Streak Freeze Reminders - Every day at 8 PM
    'send-streak-freeze-reminder': {
        'task': 'daily_challenges.tasks.send_streak_freeze_reminder',
        'schedule': crontab(hour=20, minute=0),
    },
    
    # TODO: Add more periodic tasks as needed
    # Examples:
    # - Weekly email digest
    # - Contest reminders
    # - Cache warming
    # - Analytics aggregation
    # - Cleanup tasks
}

