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


class SupportChat(models.Model):
    """Model for support chat sessions between users and admins."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('waiting', 'Waiting for Admin'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Chat details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_chats')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chats')
    subject = models.CharField(max_length=200)
    description = models.TextField(help_text="Initial issue description")
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Category and tags
    category = models.CharField(max_length=50, choices=[
        ('technical', 'Technical Issue'),
        ('billing', 'Billing & Payments'),
        ('account', 'Account Issues'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('general', 'General Inquiry'),
        ('contest', 'Contest Related'),
        ('problem', 'Problem Related'),
    ])
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    page_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Support Chat #{self.id} - {self.user.username} - {self.status}"
    
    @property
    def is_active(self):
        return self.status in ['open', 'waiting', 'in_progress']
    
    @property
    def duration(self):
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return timezone.now() - self.created_at


class ChatMessage(models.Model):
    """Model for individual chat messages."""
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File Attachment'),
        ('system', 'System Message'),
        ('code', 'Code Snippet'),
        ('link', 'Link'),
    ]
    
    # Message details
    chat = models.ForeignKey(SupportChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Content
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)  # For code snippets, links, etc.
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in Chat #{self.chat.id}"


class AdminAvailability(models.Model):
    """Model for tracking admin availability and workload."""
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability')
    is_online = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    max_concurrent_chats = models.IntegerField(default=5)
    current_chats = models.IntegerField(default=0)
    
    # Working hours
    working_hours = models.JSONField(default=dict)  # Day-wise availability
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Specializations
    specializations = models.JSONField(default=list)  # Areas of expertise
    languages = models.JSONField(default=list)  # Languages spoken
    
    # Performance metrics
    avg_response_time = models.FloatField(default=0.0)  # in minutes
    satisfaction_rating = models.FloatField(default=0.0)
    chats_resolved = models.IntegerField(default=0)
    
    # Timestamps
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Availability'
        verbose_name_plural = 'Admin Availability'
    
    def __str__(self):
        return f"{self.admin.username} - {'Online' if self.is_online else 'Offline'}"


class ChatTemplate(models.Model):
    """Model for predefined chat response templates."""
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.category}"


class ChatRating(models.Model):
    """Model for chat session ratings and feedback."""
    
    chat = models.OneToOneField(SupportChat, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_ratings')
    
    # Rating details
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    response_time_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    helpfulness_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    
    # Feedback
    feedback = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    
    # Admin performance
    admin_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    admin_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rating for Chat #{self.chat.id} - {self.overall_rating}/5" 