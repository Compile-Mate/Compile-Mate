from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """Custom User model with MateCoins and profile features."""
    
    # Profile fields
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    college = models.CharField(max_length=200, blank=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    
    # MateCoins system
    coins = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    xp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Statistics
    problems_solved = models.IntegerField(default=0)
    contests_participated = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=timezone.now)
    
    # Preferences
    preferred_language = models.CharField(
        max_length=20,
        choices=[
            ('python', 'Python'),
            ('cpp', 'C++'),
            ('java', 'Java'),
            ('javascript', 'JavaScript'),
        ],
        default='python'
    )
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )
    
    # Social features
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def add_coins(self, amount, reason="Earned"):
        """Add coins to user account and create transaction record."""
        self.coins += amount
        self.save()
        
        # Create transaction record
        CoinTransaction.objects.create(
            user=self,
            transaction_type='earn',
            amount=amount,
            reason=reason
        )
    
    def spend_coins(self, amount, reason="Spent"):
        """Spend coins from user account and create transaction record."""
        if self.coins >= amount:
            self.coins -= amount
            self.save()
            
            # Create transaction record
            CoinTransaction.objects.create(
                user=self,
                transaction_type='spend',
                amount=amount,
                reason=reason
            )
            return True
        return False
    
    def add_xp(self, amount):
        """Add XP and check for level up."""
        self.xp += amount
        self.save()
        
        # Check for level up (simple formula: level = xp // 1000 + 1)
        new_level = self.xp // 1000 + 1
        if new_level > self.level:
            self.level = new_level
            self.save()
            return True  # Leveled up
        return False
    
    def update_streak(self):
        """Update user's activity streak."""
        now = timezone.now()
        if self.last_activity.date() < now.date():
            if (now.date() - self.last_activity.date()).days == 1:
                self.current_streak += 1
            else:
                self.current_streak = 1
            
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            
            self.last_activity = now
            self.save()

    @property
    def problems_solved_count(self):
        from problems.models import Submission
        return Submission.objects.filter(user=self, status='accepted').values('problem').distinct().count()

    @property
    def total_submissions_count(self):
        from problems.models import Submission
        return Submission.objects.filter(user=self).count()

    @property
    def acceptance_rate(self):
        total = self.total_submissions_count
        accepted = Submission.objects.filter(user=self, status='accepted').count()
        return (accepted / total * 100) if total > 0 else 0

    @property
    def dynamic_streak(self):
        from problems.models import Submission
        # Get all unique days with at least one accepted submission
        days = Submission.objects.filter(user=self, status='accepted')\
            .dates('submitted_at', 'day', order='DESC')
        if not days:
            return 0
        streak = 1
        prev_day = days[0]
        for day in days[1:]:
            if (prev_day - day).days == 1:
                streak += 1
                prev_day = day
            elif (prev_day - day).days > 1:
                break
            else:
                prev_day = day
        return streak

    @property
    def longest_streak_dynamic(self):
        from problems.models import Submission
        days = list(Submission.objects.filter(user=self, status='accepted')\
            .dates('submitted_at', 'day', order='ASC'))
        if not days:
            return 0
        max_streak = 1
        current_streak = 1
        for i in range(1, len(days)):
            if (days[i] - days[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak


class CoinTransaction(models.Model):
    """Model to track all coin transactions."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coin_transactions')
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ('earn', 'Earned'),
            ('spend', 'Spent'),
        ]
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.amount} coins"


class UserAchievement(models.Model):
    """Model to track user achievements."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(
        max_length=50,
        choices=[
            ('first_solve', 'First Problem Solved'),
            ('streak_7', '7 Day Streak'),
            ('streak_30', '30 Day Streak'),
            ('solve_10', '10 Problems Solved'),
            ('solve_50', '50 Problems Solved'),
            ('solve_100', '100 Problems Solved'),
            ('contest_winner', 'Contest Winner'),
            ('perfect_score', 'Perfect Score'),
            ('early_adopter', 'Early Adopter'),
        ]
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    
    class Meta:
        unique_together = ['user', 'achievement_type']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement_type}" 