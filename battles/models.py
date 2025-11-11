from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User
from problems.models import Problem, Submission
import uuid


class Battle(models.Model):
    """Model for 1v1 code battles."""
    
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Opponent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MODE_CHOICES = [
        ('friend', 'Friend Challenge'),
        ('random', 'Random Match'),
    ]
    
    # Battle identification
    battle_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    
    # Participants
    challenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_initiated')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='battles_received')
    
    # Battle details
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='battles')
    stake = models.IntegerField(default=50, validators=[MinValueValidator(10)], help_text="MateCoins at stake")
    
    # Winner tracking
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    time_limit = models.IntegerField(default=30, help_text="Time limit in minutes")
    
    # Spectators
    spectators = models.ManyToManyField(User, related_name='watching_battles', blank=True)
    spectator_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['challenger', '-created_at']),
        ]
    
    def __str__(self):
        return f"Battle {self.battle_id}: {self.challenger.username} vs {self.opponent.username if self.opponent else 'TBD'}"
    
    @property
    def duration(self):
        """Calculate battle duration."""
        if self.started_at and self.ended_at:
            return self.ended_at - self.started_at
        return None
    
    @property
    def time_remaining(self):
        """Calculate time remaining in battle."""
        if self.started_at and self.status == 'in_progress':
            elapsed = timezone.now() - self.started_at
            limit = timezone.timedelta(minutes=self.time_limit)
            remaining = limit - elapsed
            return max(remaining, timezone.timedelta(0))
        return None
    
    def start_battle(self):
        """Start the battle."""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def end_battle(self, winner=None):
        """End the battle and determine winner."""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.winner = winner
        self.save()
        
        # Transfer coins
        if winner:
            winner.coins += self.stake
            winner.save()
            
            loser = self.opponent if winner == self.challenger else self.challenger
            loser.coins = max(0, loser.coins - self.stake)
            loser.save()


class BattleSubmission(models.Model):
    """Model for submissions made during battles."""
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='battle_submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.DurationField(help_text="Time taken from battle start")
    
    class Meta:
        ordering = ['submitted_at']
        unique_together = ['battle', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.battle.battle_id} - {self.submission.status}"


class BattleInvitation(models.Model):
    """Model for friend battle invitations."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_invitations_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_invitations_received')
    battle = models.OneToOneField(Battle, on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    stake = models.IntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}: {self.status}"
    
    def accept(self):
        """Accept the invitation and create battle."""
        if self.status == 'pending' and timezone.now() < self.expires_at:
            from battles.models import Battle
            battle = Battle.objects.create(
                mode='friend',
                challenger=self.from_user,
                opponent=self.to_user,
                problem=self.problem,
                stake=self.stake
            )
            self.battle = battle
            self.status = 'accepted'
            self.save()
            return battle
        return None
    
    def decline(self):
        """Decline the invitation."""
        self.status = 'declined'
        self.save()


class BattleStats(models.Model):
    """Model for tracking user battle statistics."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='battle_stats')
    total_battles = models.IntegerField(default=0)
    battles_won = models.IntegerField(default=0)
    battles_lost = models.IntegerField(default=0)
    win_streak = models.IntegerField(default=0)
    best_win_streak = models.IntegerField(default=0)
    total_coins_won = models.IntegerField(default=0)
    total_coins_lost = models.IntegerField(default=0)
    fastest_solve = models.DurationField(null=True, blank=True, help_text="Fastest problem solve in battle")
    
    class Meta:
        verbose_name_plural = 'Battle stats'
    
    def __str__(self):
        return f"{self.user.username} - {self.battles_won}W/{self.battles_lost}L"
    
    @property
    def win_rate(self):
        """Calculate win rate percentage."""
        if self.total_battles > 0:
            return (self.battles_won / self.total_battles) * 100
        return 0.0
    
    def update_stats(self, battle, won):
        """Update stats after a battle."""
        self.total_battles += 1
        if won:
            self.battles_won += 1
            self.win_streak += 1
            self.best_win_streak = max(self.best_win_streak, self.win_streak)
            self.total_coins_won += battle.stake
        else:
            self.battles_lost += 1
            self.win_streak = 0
            self.total_coins_lost += battle.stake
        self.save()
