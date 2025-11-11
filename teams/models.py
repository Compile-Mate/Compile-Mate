from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User
from problems.models import Problem
import uuid


class Team(models.Model):
    """Model for coding teams/clans."""
    
    team_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Visual
    avatar_url = models.URLField(blank=True)
    banner_url = models.URLField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    # Leadership
    founder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='founded_teams')
    leaders = models.ManyToManyField(User, related_name='leading_teams', blank=True)
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams')
    
    # Settings
    is_public = models.BooleanField(default=True)
    is_recruiting = models.BooleanField(default=True)
    max_members = models.IntegerField(default=50, validators=[MinValueValidator(5), MaxValueValidator(100)])
    
    # Stats
    total_coins = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_xp']
        indexes = [
            models.Index(fields=['-total_xp']),
            models.Index(fields=['is_public', '-total_xp']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members


class TeamMembership(models.Model):
    """Model for team membership."""
    
    ROLE_CHOICES = [
        ('founder', 'Founder'),
        ('leader', 'Leader'),
        ('member', 'Member'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    contribution_score = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['team', 'user']
        ordering = ['-contribution_score']
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"


class TeamInvitation(models.Model):
    """Model for team invitations."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_invitations_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_invitations_received')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team', 'to_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team.name} -> {self.to_user.username}: {self.status}"
    
    def accept(self):
        """Accept the invitation and add user to team."""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            # Add user to team
            TeamMembership.objects.create(
                team=self.team,
                user=self.to_user,
                role='member'
            )
            return True
        return False
    
    def decline(self):
        """Decline the invitation."""
        if self.status == 'pending':
            self.status = 'declined'
            self.save()
            return True
        return False


class TeamContest(models.Model):
    """Model for team-only contests."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    participating_teams = models.ManyToManyField(Team, related_name='team_contests')
    problems = models.ManyToManyField(Problem, related_name='team_contests')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    prize_pool = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return self.name


class TeamAchievement(models.Model):
    """Model for team achievements."""
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.team.name} - {self.name}"
