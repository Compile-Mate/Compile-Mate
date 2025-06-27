from django.db import models
from django.utils import timezone
from users.models import User


class Notification(models.Model):
    """Model for user notifications."""
    
    TYPE_CHOICES = [
        ('achievement', 'Achievement'),
        ('contest', 'Contest'),
        ('reward', 'Reward'),
        ('system', 'System'),
        ('social', 'Social'),
    ]
    
    # Notification details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    related_url = models.URLField(blank=True, help_text="URL to related content")
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class SiteSettings(models.Model):
    """Model for site-wide settings."""
    
    # Site information
    site_name = models.CharField(max_length=100, default='CompileMate')
    site_description = models.TextField(blank=True)
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Features
    enable_registration = models.BooleanField(default=True)
    enable_social_login = models.BooleanField(default=True)
    enable_contests = models.BooleanField(default=True)
    enable_rewards = models.BooleanField(default=True)
    
    # MateCoins settings
    initial_coins = models.IntegerField(default=100)
    coins_per_accepted_solution = models.IntegerField(default=10)
    coins_per_hard_problem = models.IntegerField(default=25)
    coins_per_contest_participation = models.IntegerField(default=50)
    coins_per_weekly_streak = models.IntegerField(default=100)
    
    # Contest settings
    default_contest_duration = models.DurationField(default=timezone.timedelta(hours=2))
    max_contest_problems = models.IntegerField(default=6)
    
    # Judge settings
    default_time_limit = models.FloatField(default=1.0)
    default_memory_limit = models.IntegerField(default=128)
    
    # Social features
    enable_following = models.BooleanField(default=True)
    enable_discussions = models.BooleanField(default=True)
    enable_achievements = models.BooleanField(default=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return 'Site Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class UserActivity(models.Model):
    """Model for tracking user activities."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('problem_solve', 'Problem Solved'),
        ('contest_join', 'Contest Joined'),
        ('contest_win', 'Contest Won'),
        ('reward_earn', 'Reward Earned'),
        ('achievement', 'Achievement Unlocked'),
        ('profile_update', 'Profile Updated'),
        ('discussion_post', 'Discussion Post'),
    ]
    
    # Activity details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    
    # Related data
    related_data = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class FAQ(models.Model):
    """Model for frequently asked questions."""
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """Model for contact form messages."""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    # Message details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class SystemLog(models.Model):
    """Model for system logs."""
    
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Log details
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # Context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level.upper()} - {self.message[:50]}" 