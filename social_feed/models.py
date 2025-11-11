from django.db import models
from django.utils import timezone
from users.models import User
from problems.models import Problem, Submission


class Post(models.Model):
    """Model for social feed posts."""
    
    POST_TYPE_CHOICES = [
        ('achievement', 'Achievement'),
        ('solution', 'Solution Share'),
        ('question', 'Question'),
        ('discussion', 'Discussion'),
        ('milestone', 'Milestone'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES)
    content = models.TextField()
    
    # Optional related objects
    problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    # Engagement
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username} - {self.post_type} - {self.created_at.strftime('%Y-%m-%d')}"


class Comment(models.Model):
    """Model for comments on posts."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Engagement
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    likes_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class Follow(models.Model):
    """Model for user follows."""
    
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Activity(models.Model):
    """Model for user activity feed."""
    
    ACTIVITY_TYPE_CHOICES = [
        ('solved_problem', 'Solved Problem'),
        ('earned_badge', 'Earned Badge'),
        ('joined_contest', 'Joined Contest'),
        ('won_battle', 'Won Battle'),
        ('streak_milestone', 'Streak Milestone'),
        ('level_up', 'Level Up'),
        ('created_post', 'Created Post'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    
    # Optional related data
    related_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at.strftime('%Y-%m-%d')}"


class Notification(models.Model):
    """Enhanced notification model for social interactions."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('share', 'Share'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    
    # Related objects
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.notification_type}"
