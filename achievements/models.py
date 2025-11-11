from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User


class BadgeCategory(models.Model):
    """Model for organizing badges into categories."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="🏅")
    display_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Badge categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Badge(models.Model):
    """Model for achievements and badges."""
    
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
        ('legendary', 'Legendary'),
    ]
    
    BADGE_TYPE_CHOICES = [
        ('problem_solving', 'Problem Solving'),
        ('streak', 'Streak'),
        ('contest', 'Contest'),
        ('battle', 'Battle'),
        ('social', 'Social'),
        ('special', 'Special'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField()
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    badge_type = models.CharField(max_length=30, choices=BADGE_TYPE_CHOICES)
    category = models.ForeignKey(BadgeCategory, on_delete=models.CASCADE, related_name='badges', null=True, blank=True)
    
    # Visual
    icon = models.CharField(max_length=100, help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    image_url = models.URLField(blank=True, help_text="Optional badge image URL")
    
    # Requirements
    requirement_type = models.CharField(max_length=50, help_text="Type of requirement (e.g., problems_solved, streak_days)")
    requirement_value = models.IntegerField(help_text="Value needed to unlock (e.g., 100 for 100 problems)")
    requirement_description = models.TextField(help_text="Human-readable requirement")
    
    # Rewards
    coin_reward = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    xp_reward = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Metadata
    is_active = models.BooleanField(default=True)
    is_secret = models.BooleanField(default=False, help_text="Hidden until unlocked")
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', 'tier', 'name']
        indexes = [
            models.Index(fields=['badge_type', 'is_active']),
            models.Index(fields=['tier']),
        ]
    
    def __str__(self):
        return f"{self.icon} {self.name} ({self.tier})"
    
    @property
    def tier_color(self):
        """Get color based on tier."""
        colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0',
            'gold': '#FFD700',
            'platinum': '#E5E4E2',
            'diamond': '#B9F2FF',
            'legendary': '#FF6B6B',
        }
        return colors.get(self.tier, self.color)


class UserBadge(models.Model):
    """Model for tracking badges earned by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Progress towards next tier")
    is_displayed = models.BooleanField(default=False, help_text="Display on profile")
    is_new = models.BooleanField(default=True, help_text="Show 'NEW' indicator")
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', '-earned_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
    def mark_as_seen(self):
        """Mark badge as seen (remove NEW indicator)."""
        self.is_new = False
        self.save()


class Achievement(models.Model):
    """Model for tracking specific achievements (can unlock multiple times)."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    achievement_type = models.CharField(max_length=50)
    requirement_description = models.TextField()
    
    # Rewards
    coin_reward = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=0)
    
    # Repeatability
    is_repeatable = models.BooleanField(default=False)
    max_completions = models.IntegerField(null=True, blank=True, help_text="Max times this can be completed")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """Model for tracking achievements completed by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements')
    completed_at = models.DateTimeField(auto_now_add=True)
    completion_count = models.IntegerField(default=1, help_text="Number of times completed")
    
    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', '-completed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name} (x{self.completion_count})"


class BadgeProgress(models.Model):
    """Model for tracking user progress towards badges."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badge_progress')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='progress_tracking')
    current_value = models.IntegerField(default=0)
    target_value = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        verbose_name_plural = 'Badge progress'
        indexes = [
            models.Index(fields=['user', 'badge']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}: {self.current_value}/{self.target_value}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100)
        return 0
    
    @property
    def is_complete(self):
        """Check if badge requirement is met."""
        return self.current_value >= self.target_value
    
    def update_progress(self, new_value):
        """Update progress and check if badge should be awarded."""
        self.current_value = new_value
        self.save()
        
        if self.is_complete:
            # Award badge
            user_badge, created = UserBadge.objects.get_or_create(
                user=self.user,
                badge=self.badge
            )
            
            if created:
                # Award rewards
                self.user.coins += self.badge.coin_reward
                self.user.xp += self.badge.xp_reward
                self.user.save()
                
                # Create notification
                from core.models import Notification
                Notification.objects.create(
                    user=self.user,
                    title=f"🏆 Badge Unlocked: {self.badge.name}",
                    message=f"Congratulations! You've earned the {self.badge.tier.title()} badge: {self.badge.name}!",
                    notification_type='achievement'
                )
                
                return user_badge
        return None


class Milestone(models.Model):
    """Model for special milestones."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    milestone_type = models.CharField(max_length=50)
    threshold = models.IntegerField()
    
    # Rewards
    coin_reward = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=0)
    special_badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['milestone_type', 'threshold']
    
    def __str__(self):
        return f"{self.icon} {self.name} ({self.threshold})"


class UserMilestone(models.Model):
    """Model for tracking milestones achieved by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='user_milestones')
    achieved_at = models.DateTimeField(auto_now_add=True)
    value_achieved = models.IntegerField()
    
    class Meta:
        unique_together = ['user', 'milestone']
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.milestone.name}"
