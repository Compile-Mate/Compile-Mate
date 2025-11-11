from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from problems.models import Problem


class LearningPath(models.Model):
    """Model for curated learning paths."""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Visual
    thumbnail_url = models.URLField(blank=True)
    banner_url = models.URLField(blank=True)
    icon = models.CharField(max_length=100, default="📚")
    color = models.CharField(max_length=7, default='#3B82F6')
    
    # Content
    topics = models.ManyToManyField('Topic', related_name='learning_paths')
    estimated_duration = models.IntegerField(help_text="Estimated hours to complete")
    
    # Rewards
    completion_reward_coins = models.IntegerField(default=500)
    completion_reward_xp = models.IntegerField(default=1000)
    certificate_awarded = models.BooleanField(default=True)
    
    # Stats
    enrolled_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    # Metadata
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_paths')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-enrolled_count']
        indexes = [
            models.Index(fields=['is_published', '-enrolled_count']),
        ]
    
    def __str__(self):
        return f"{self.icon} {self.title}"
    
    @property
    def completion_rate(self):
        if self.enrolled_count > 0:
            return (self.completed_count / self.enrolled_count) * 100
        return 0.0


class Topic(models.Model):
    """Model for learning topics."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class PathModule(models.Model):
    """Model for modules within a learning path."""
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField()
    
    # Content
    problems = models.ManyToManyField(Problem, through='ModuleProblem', related_name='path_modules')
    video_url = models.URLField(blank=True)
    reading_material = models.TextField(blank=True)
    
    # Requirements
    is_locked = models.BooleanField(default=False, help_text="Requires previous modules to be completed")
    
    class Meta:
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.title} - Module {self.order}: {self.title}"


class ModuleProblem(models.Model):
    """Intermediate model for problems in modules."""
    
    module = models.ForeignKey(PathModule, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_optional = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['module', 'order']
        unique_together = ['module', 'problem']
    
    def __str__(self):
        return f"{self.module} - {self.problem.title}"


class PathEnrollment(models.Model):
    """Model for user enrollment in learning paths."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_enrollments')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Progress tracking
    current_module = models.ForeignKey(PathModule, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_students')
    completed_modules = models.ManyToManyField(PathModule, related_name='completed_by', blank=True)
    progress_percentage = models.FloatField(default=0.0)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'learning_path']
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', '-last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title} ({self.status})"
    
    def update_progress(self):
        """Calculate and update progress percentage."""
        total_modules = self.learning_path.modules.count()
        if total_modules > 0:
            completed = self.completed_modules.count()
            self.progress_percentage = (completed / total_modules) * 100
            self.save()


class PathRating(models.Model):
    """Model for rating learning paths."""
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['learning_path', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title}: {self.rating}⭐"


class Editorial(models.Model):
    """Model for problem editorials/tutorials."""
    
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='editorial')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='editorials')
    
    # Content
    title = models.CharField(max_length=200)
    intuition = models.TextField(help_text="High-level approach")
    approach = models.TextField(help_text="Detailed explanation")
    complexity_analysis = models.TextField(help_text="Time and space complexity")
    code_walkthrough = models.TextField(help_text="Line-by-line explanation")
    
    # Video
    video_url = models.URLField(blank=True)
    video_duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    
    # Code examples
    example_code = models.JSONField(default=dict, help_text="Code examples in different languages")
    
    # Engagement
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_editorials', blank=True)
    likes_count = models.IntegerField(default=0)
    
    # Metadata
    is_official = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Editorial: {self.problem.title} by {self.author.username}"
