from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User


class Tag(models.Model):
    """Model for problem tags/categories."""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Problem(models.Model):
    """Model for coding problems/challenges."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(help_text="Problem description, examples, input/output format")
    constraints = models.TextField(blank=True, help_text="Problem constraints (one per line)")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Problem details
    starter_code = models.JSONField(default=dict, help_text="Starter code for different languages")
    
    # Statistics
    total_submissions = models.IntegerField(default=0)
    accepted_submissions = models.IntegerField(default=0)
    acceptance_rate = models.FloatField(default=0.0)
    average_time = models.FloatField(default=0.0, help_text="Average execution time in seconds")
    average_memory = models.FloatField(default=0.0, help_text="Average memory usage in MB")
    
    # Metadata
    tags = models.ManyToManyField(Tag, related_name='problems')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rewards
    coin_reward = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    xp_reward = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Calculate acceptance rate
        if self.total_submissions > 0:
            self.acceptance_rate = (self.accepted_submissions / self.total_submissions) * 100
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def difficulty_color(self):
        colors = {
            'easy': '#10B981',  # Green
            'medium': '#F59E0B',  # Yellow
            'hard': '#EF4444',  # Red
        }
        return colors.get(self.difficulty, '#6B7280')


class TestCase(models.Model):
    """Model for problem test cases."""
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False, help_text="Hidden test cases are not shown to users")
    time_limit = models.FloatField(default=1.0, help_text="Time limit in seconds")
    memory_limit = models.IntegerField(default=128, help_text="Memory limit in MB")
    order = models.IntegerField(default=0, help_text="Order of test case")
    
    class Meta:
        ordering = ['problem', 'order']
        unique_together = ['problem', 'order']
    
    def __str__(self):
        return f"{self.problem.title} - Test Case {self.order}"


class Submission(models.Model):
    """Model for code submissions."""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('memory_limit_exceeded', 'Memory Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compilation_error', 'Compilation Error'),
        ('internal_error', 'Internal Error'),
    ]
    
    # Submission details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    
    # Results
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    memory_used = models.FloatField(null=True, blank=True, help_text="Memory used in MB")
    test_cases_passed = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    
    # Error details
    error_message = models.TextField(blank=True)
    failed_test_case = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    judged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        if self.status != 'pending' and not self.judged_at:
            self.judged_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_accepted(self):
        return self.status == 'accepted'
    
    @property
    def is_first_accepted(self):
        """Check if this is the user's first accepted submission for this problem."""
        if not self.is_accepted:
            return False
        return not Submission.objects.filter(
            user=self.user,
            problem=self.problem,
            status='accepted',
            submitted_at__lt=self.submitted_at
        ).exists()


class ProblemDiscussion(models.Model):
    """Model for problem discussions and comments."""
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    is_solution = models.BooleanField(default=False, help_text="Mark as official solution")
    upvotes = models.ManyToManyField(User, related_name='upvoted_discussions', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_discussions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.content[:50]}"
    
    @property
    def vote_count(self):
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def is_reply(self):
        return self.parent is not None 