from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from users.models import User
from problems.models import Problem, Submission


class DailyChallengeManager(models.Manager):
    def get_today_challenge(self):
        """Get or create today's challenge."""
        today = timezone.now().date()
        challenge, created = self.get_or_create(
            date=today,
            defaults={'problem': self._select_daily_problem()}
        )
        return challenge
    
    def _select_daily_problem(self):
        """Select a random problem for daily challenge."""
        # Select medium difficulty problem that hasn't been used recently
        from django.db.models import Q
        import random
        
        recent_challenges = self.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).values_list('problem_id', flat=True)
        
        problems = Problem.objects.filter(
            status='published',
            difficulty='medium'
        ).exclude(id__in=recent_challenges)
        
        if problems.exists():
            return random.choice(problems)
        return Problem.objects.filter(status='published').first()


class DailyChallenge(models.Model):
    """Model for daily coding challenges."""
    
    date = models.DateField(unique=True, db_index=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='daily_challenges')
    bonus_coins = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    bonus_xp = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    participants_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = DailyChallengeManager()
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"Daily Challenge - {self.date} - {self.problem.title}"
    
    @property
    def completion_rate(self):
        """Calculate completion rate percentage."""
        if self.participants_count > 0:
            return (self.completed_count / self.participants_count) * 100
        return 0.0
    
    @property
    def is_today(self):
        """Check if this is today's challenge."""
        return self.date == timezone.now().date()
    
    @property
    def is_active(self):
        """Check if challenge is still active (today)."""
        return self.is_today


class DailyChallengeParticipation(models.Model):
    """Model for tracking user participation in daily challenges."""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_challenge_participations')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    coins_earned = models.IntegerField(default=0)
    xp_earned = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'challenge']
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.date} - {self.status}"
    
    def complete(self, submission):
        """Mark challenge as completed."""
        self.status = 'completed'
        self.submission = submission
        self.completed_at = timezone.now()
        self.time_taken = self.completed_at - self.started_at
        self.coins_earned = self.challenge.bonus_coins
        self.xp_earned = self.challenge.bonus_xp
        self.save()
        
        # Update challenge counts
        self.challenge.completed_count += 1
        self.challenge.save()
        
        # Update user streak
        streak_stats, _ = StreakStats.objects.get_or_create(user=self.user)
        streak_stats.update_streak()
        
        # Award coins and XP
        self.user.coins += self.coins_earned
        self.user.xp += self.xp_earned
        self.user.save()


class StreakStats(models.Model):
    """Model for tracking user streaks."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak_stats')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_challenges_completed = models.IntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)
    streak_freeze_count = models.IntegerField(default=0, help_text="Number of streak freeze items owned")
    
    class Meta:
        verbose_name_plural = 'Streak stats'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"
    
    def update_streak(self):
        """Update user's streak after completing a challenge."""
        today = timezone.now().date()
        
        if self.last_completed_date is None:
            # First challenge
            self.current_streak = 1
        elif self.last_completed_date == today:
            # Already completed today, no change
            return
        elif self.last_completed_date == today - timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
        else:
            # Streak broken
            self.current_streak = 1
        
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_completed_date = today
        self.total_challenges_completed += 1
        self.save()
        
        # Check for streak milestone achievements
        self._check_streak_milestones()
    
    def _check_streak_milestones(self):
        """Check and award streak milestone achievements."""
        milestones = [7, 30, 50, 100, 365]
        for milestone in milestones:
            if self.current_streak == milestone:
                # Award achievement (will be handled by achievements app)
                from core.models import Notification
                Notification.objects.create(
                    user=self.user,
                    title=f"🔥 {milestone} Day Streak!",
                    message=f"Amazing! You've maintained a {milestone} day coding streak!",
                    notification_type='achievement'
                )
    
    def use_streak_freeze(self):
        """Use a streak freeze item."""
        if self.streak_freeze_count > 0:
            self.streak_freeze_count -= 1
            self.last_completed_date = timezone.now().date()
            self.save()
            return True
        return False
    
    def can_use_freeze(self):
        """Check if user can use a streak freeze."""
        if self.streak_freeze_count <= 0:
            return False
        today = timezone.now().date()
        if self.last_completed_date and self.last_completed_date < today - timedelta(days=1):
            return True
        return False


class StreakFreezeItem(models.Model):
    """Model for streak freeze items (purchasable with coins)."""
    
    name = models.CharField(max_length=100, default="Streak Freeze")
    description = models.TextField(default="Protects your streak for one day if you miss a challenge")
    cost_in_coins = models.IntegerField(default=200, validators=[MinValueValidator(1)])
    icon = models.CharField(max_length=50, default="❄️")
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Streak Freeze Item'
        verbose_name_plural = 'Streak Freeze Items'
    
    def __str__(self):
        return f"{self.name} ({self.cost_in_coins} coins)"


class StreakFreezePurchase(models.Model):
    """Model for tracking streak freeze purchases."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streak_freeze_purchases')
    item = models.ForeignKey(StreakFreezeItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_cost = models.IntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quantity}x Streak Freeze"
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = self.item.cost_in_coins * self.quantity
        
        # Deduct coins from user
        if self.pk is None:  # Only on creation
            self.user.coins -= self.total_cost
            self.user.save()
            
            # Add to user's streak freeze count
            streak_stats, _ = StreakStats.objects.get_or_create(user=self.user)
            streak_stats.streak_freeze_count += self.quantity
            streak_stats.save()
        
        super().save(*args, **kwargs)


class DailyChallengeLeaderboard(models.Model):
    """Model for daily challenge leaderboard (fastest solvers)."""
    
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='leaderboard')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rank = models.IntegerField()
    time_taken = models.DurationField()
    completed_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['challenge', 'user']
        ordering = ['challenge', 'rank']
        indexes = [
            models.Index(fields=['challenge', 'rank']),
        ]
    
    def __str__(self):
        return f"{self.challenge.date} - Rank {self.rank}: {self.user.username}"
