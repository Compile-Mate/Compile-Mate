from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User
from problems.models import Problem, Submission


class Contest(models.Model):
    """Model for coding contests."""
    
    TYPE_CHOICES = [
        ('weekly', 'Weekly Contest'),
        ('monthly', 'Monthly Contest'),
        ('special', 'Special Contest'),
        ('practice', 'Practice Contest'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    contest_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField(help_text="Contest duration in hours")
    
    # Problems
    problems = models.ManyToManyField(Problem, through='ContestProblem', related_name='contests')
    
    # Participants
    participants = models.ManyToManyField(User, through='ContestParticipation', related_name='contests')
    
    # Settings
    is_rated = models.BooleanField(default=True, help_text="Whether this contest affects ratings")
    allow_registration = models.BooleanField(default=True)
    max_participants = models.IntegerField(null=True, blank=True, help_text="Maximum number of participants")
    
    # Rewards
    total_prize_pool = models.IntegerField(default=0, help_text="Total prize pool in coins")
    prize_distribution = models.JSONField(default=dict, help_text="Prize distribution for top participants")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_upcoming(self):
        return timezone.now() < self.start_time
    
    @property
    def is_ended(self):
        return timezone.now() > self.end_time
    
    @property
    def time_remaining(self):
        if self.is_active:
            return self.end_time - timezone.now()
        elif self.is_upcoming:
            return self.start_time - timezone.now()
        return None
    
    @property
    def participants_count(self):
        return self.participants.count()


class ContestProblem(models.Model):
    """Intermediate model for contest problems with ordering and scoring."""
    
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.IntegerField(help_text="Order of problem in contest")
    points = models.IntegerField(default=100, help_text="Points for solving this problem")
    is_visible = models.BooleanField(default=True, help_text="Whether problem is visible to participants")
    
    class Meta:
        unique_together = ['contest', 'problem']
        ordering = ['contest', 'order']
    
    def __str__(self):
        return f"{self.contest.title} - {self.problem.title}"


class ContestParticipation(models.Model):
    """Model for contest participation and results."""
    
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    solved_problems = models.ManyToManyField(Problem, through='ContestSubmission')
    
    class Meta:
        unique_together = ['contest', 'user']
        ordering = ['-score', 'joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.contest.title}"
    
    def calculate_score(self):
        """Calculate total score based on solved problems."""
        total_score = 0
        for submission in self.contestsubmission_set.filter(status='accepted'):
            contest_problem = ContestProblem.objects.get(
                contest=self.contest,
                problem=submission.problem
            )
            total_score += contest_problem.points
        
        self.score = total_score
        self.save()
        return total_score


class ContestSubmission(models.Model):
    """Model for submissions made during contests."""
    
    participation = models.ForeignKey(ContestParticipation, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=Submission.STATUS_CHOICES)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.participation.user.username} - {self.problem.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Update status from the related submission
        if self.submission:
            self.status = self.submission.status
        super().save(*args, **kwargs)


class ContestLeaderboard(models.Model):
    """Model for contest leaderboard entries."""
    
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='leaderboard_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rank = models.IntegerField()
    score = models.IntegerField()
    problems_solved = models.IntegerField(default=0)
    total_time = models.DurationField(default=timezone.timedelta)
    last_submission = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['contest', 'user']
        ordering = ['contest', 'rank']
    
    def __str__(self):
        return f"{self.contest.title} - {self.user.username} (Rank {self.rank})"


class ContestAnnouncement(models.Model):
    """Model for contest announcements."""
    
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contest.title} - {self.title}" 