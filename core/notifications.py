"""
Real-time notification system for CompileMate.
Handles creating and sending notifications to users.
"""

from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.models import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manager for creating and sending notifications."""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, related_url='', **kwargs):
        """
        Create a notification for a user.
        
        Args:
            user: User object
            notification_type: Type of notification (achievement, contest, reward, system, social)
            title: Notification title
            message: Notification message
            related_url: URL to related content
            **kwargs: Additional data (related_object_id, related_object_type)
        """
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_url=related_url,
                related_object_id=kwargs.get('related_object_id'),
                related_object_type=kwargs.get('related_object_type')
            )
            
            # Send real-time notification via WebSocket
            NotificationManager.send_realtime_notification(user.id, notification)
            
            # Invalidate user's notification cache
            cache.delete(f"unread_notifications:{user.id}")
            
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def send_realtime_notification(user_id, notification):
        """Send real-time notification via WebSocket."""
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}",
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': notification.id,
                            'type': notification.notification_type,
                            'title': notification.title,
                            'message': notification.message,
                            'url': notification.related_url,
                            'is_read': notification.is_read,
                            'created_at': notification.created_at.isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            
            # Invalidate cache
            cache.delete(f"unread_notifications:{user.id}")
            
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user."""
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        cache.delete(f"unread_notifications:{user.id}")
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications."""
        cache_key = f"unread_notifications:{user.id}"
        count = cache.get(cache_key)
        
        if count is None:
            count = Notification.objects.filter(user=user, is_read=False).count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
        
        return count
    
    @staticmethod
    def notify_achievement(user, achievement_type, description):
        """Send achievement notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='achievement',
            title='🏆 Achievement Unlocked!',
            message=description,
            related_url='/profile/',
            related_object_type='achievement',
        )
    
    @staticmethod
    def notify_contest_start(user, contest):
        """Send contest start notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='contest',
            title=f'Contest Starting: {contest.title}',
            message=f'The contest "{contest.title}" is about to start!',
            related_url=f'/contests/{contest.id}/',
            related_object_id=contest.id,
            related_object_type='contest',
        )
    
    @staticmethod
    def notify_submission_result(user, submission):
        """Send submission result notification."""
        status_emoji = {
            'accepted': '✅',
            'wrong_answer': '❌',
            'time_limit_exceeded': '⏱️',
            'runtime_error': '💥',
            'compilation_error': '🔧'
        }
        
        emoji = status_emoji.get(submission.status, '📝')
        
        return NotificationManager.create_notification(
            user=user,
            notification_type='system',
            title=f'{emoji} Submission Result',
            message=f'Your submission for "{submission.problem.title}" - {submission.get_status_display()}',
            related_url=f'/problems/{submission.problem.slug}/submissions/{submission.id}/',
            related_object_id=submission.id,
            related_object_type='submission',
        )
    
    @staticmethod
    def notify_coin_reward(user, amount, reason):
        """Send coin reward notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='reward',
            title='🪙 MateCoins Earned!',
            message=f'You earned {amount} MateCoins! {reason}',
            related_url='/rewards/',
        )
    
    @staticmethod
    def notify_level_up(user, new_level):
        """Send level up notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='achievement',
            title=f'🎉 Level {new_level} Achieved!',
            message=f'Congratulations! You\'ve reached level {new_level}!',
            related_url='/profile/',
        )
    
    @staticmethod
    def notify_streak_milestone(user, streak_days):
        """Send streak milestone notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='achievement',
            title=f'🔥 {streak_days} Day Streak!',
            message=f'Amazing! You\'ve maintained a {streak_days}-day solving streak!',
            related_url='/profile/',
        )
    
    @staticmethod
    def notify_contest_winner(user, contest, rank):
        """Send contest winner notification."""
        medals = {1: '🥇', 2: '🥈', 3: '🥉'}
        medal = medals.get(rank, '🏆')
        
        return NotificationManager.create_notification(
            user=user,
            notification_type='contest',
            title=f'{medal} Contest Completed!',
            message=f'You ranked #{rank} in "{contest.title}"!',
            related_url=f'/contests/{contest.id}/leaderboard/',
            related_object_id=contest.id,
            related_object_type='contest',
        )
    
    @staticmethod
    def notify_new_follower(user, follower):
        """Send new follower notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='social',
            title='👤 New Follower',
            message=f'{follower.username} started following you!',
            related_url=f'/profile/{follower.username}/',
            related_object_id=follower.id,
            related_object_type='user',
        )
    
    @staticmethod
    def notify_discussion_reply(user, reply, discussion):
        """Send discussion reply notification."""
        return NotificationManager.create_notification(
            user=user,
            notification_type='social',
            title='💬 New Reply',
            message=f'{reply.user.username} replied to your discussion',
            related_url=f'/problems/{discussion.problem.slug}/#discussion-{discussion.id}',
            related_object_id=discussion.id,
            related_object_type='discussion',
        )


def send_bulk_notifications(users, notification_type, title, message, **kwargs):
    """Send notifications to multiple users at once."""
    notifications = []
    for user in users:
        notification = NotificationManager.create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
        if notification:
            notifications.append(notification)
    return notifications

