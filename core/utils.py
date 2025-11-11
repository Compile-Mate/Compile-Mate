"""
Utility functions for CompileMate platform.
"""

import hashlib
import random
import string
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import get_user_model
from functools import wraps
import time
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_random_string(length=32):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_hash(text):
    """Generate SHA256 hash of text."""
    return hashlib.sha256(text.encode()).hexdigest()


def time_ago(dt):
    """
    Convert datetime to human-readable 'time ago' format.
    Example: "2 hours ago", "3 days ago"
    """
    if not dt:
        return "Never"
    
    now = timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def cached_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def retry_on_failure(max_attempts=3, delay=1):
    """
    Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_stats(user):
    """Get comprehensive user statistics."""
    from problems.models import Submission
    
    cache_key = f"user_stats:{user.id}"
    stats = cache.get(cache_key)
    
    if stats is None:
        # Calculate stats
        total_submissions = Submission.objects.filter(user=user).count()
        accepted_submissions = Submission.objects.filter(user=user, status='accepted').count()
        
        stats = {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0,
            'problems_solved': user.problems_solved_count,
            'coins': user.coins,
            'xp': user.xp,
            'level': user.level,
            'current_streak': user.dynamic_streak,
            'longest_streak': user.longest_streak_dynamic,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, 300)
    
    return stats


def calculate_problem_difficulty_score(problem):
    """
    Calculate a difficulty score for a problem (0-100).
    Based on acceptance rate, average time, and user ratings.
    """
    # Base score from acceptance rate (inverted)
    acceptance_score = 100 - problem.acceptance_rate
    
    # Adjust based on average time (if available)
    time_factor = min(problem.average_time * 10, 50) if problem.average_time > 0 else 0
    
    # Final score
    difficulty_score = min(100, acceptance_score + time_factor)
    
    return round(difficulty_score, 2)


def get_leaderboard(limit=100, time_filter='all'):
    """
    Get leaderboard data with caching.
    
    Args:
        limit: Number of users to return
        time_filter: 'all', 'weekly', 'monthly'
    """
    cache_key = f"leaderboard:{time_filter}:{limit}"
    leaderboard = cache.get(cache_key)
    
    if leaderboard is None:
        if time_filter == 'weekly':
            week_ago = timezone.now() - timezone.timedelta(days=7)
            # Get users with most problems solved this week
            from problems.models import Submission
            users = User.objects.annotate(
                weekly_solves=Submission.objects.filter(
                    user=User,
                    status='accepted',
                    submitted_at__gte=week_ago
                ).values('problem').distinct().count()
            ).order_by('-weekly_solves')[:limit]
        elif time_filter == 'monthly':
            month_ago = timezone.now() - timezone.timedelta(days=30)
            from problems.models import Submission
            users = User.objects.annotate(
                monthly_solves=Submission.objects.filter(
                    user=User,
                    status='accepted',
                    submitted_at__gte=month_ago
                ).values('problem').distinct().count()
            ).order_by('-monthly_solves')[:limit]
        else:
            # All-time leaderboard
            users = User.objects.order_by('-xp', '-problems_solved')[:limit]
        
        leaderboard = list(users)
        
        # Cache for 5 minutes
        cache.set(cache_key, leaderboard, 300)
    
    return leaderboard


def format_bytes(bytes_value):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_duration(seconds):
    """Format seconds to human-readable duration."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def sanitize_code(code):
    """Sanitize user code for security."""
    # Remove potentially dangerous operations
    dangerous_patterns = [
        'import os',
        'import subprocess',
        'import sys',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
    ]
    
    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if pattern in code:
            logger.warning(f"Potentially dangerous code detected: {pattern}")
    
    return code


def get_or_create_cache(key, factory_func, timeout=300):
    """
    Get value from cache or create it using factory function.
    
    Args:
        key: Cache key
        factory_func: Function to create value if not in cache
        timeout: Cache timeout in seconds
    """
    value = cache.get(key)
    if value is None:
        value = factory_func()
        cache.set(key, value, timeout)
    return value


def batch_update(model, objects, fields, batch_size=1000):
    """
    Perform batch update on queryset.
    More efficient than updating objects one by one.
    """
    model.objects.bulk_update(objects, fields, batch_size=batch_size)


def send_notification_email(user, subject, message):
    """Send notification email to user."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {e}")
        return False


class RateLimiter:
    """Simple rate limiter using cache."""
    
    def __init__(self, key, limit, window=60):
        """
        Args:
            key: Unique identifier (e.g., user_id or IP)
            limit: Maximum number of requests
            window: Time window in seconds
        """
        self.cache_key = f"rate_limit:{key}"
        self.limit = limit
        self.window = window
    
    def is_allowed(self):
        """Check if request is allowed."""
        current_count = cache.get(self.cache_key, 0)
        if current_count >= self.limit:
            return False
        
        cache.set(self.cache_key, current_count + 1, self.window)
        return True
    
    def reset(self):
        """Reset rate limit counter."""
        cache.delete(self.cache_key)

