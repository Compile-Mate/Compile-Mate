from django.db import models
from django.utils import timezone
from problems.models import Problem, TestCase, Submission


class JudgeSubmission(models.Model):
    """Model for tracking judge submissions and results."""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Submission details
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='judge_submission')
    judge_id = models.CharField(max_length=100, unique=True, help_text="Judge0 submission ID")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    results = models.JSONField(default=list, help_text="Test case results from judge")
    compilation_output = models.TextField(blank=True)
    execution_output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Judge Submission {self.judge_id} - {self.submission.problem.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)


class TestCaseResult(models.Model):
    """Model for individual test case results."""
    
    judge_submission = models.ForeignKey(JudgeSubmission, on_delete=models.CASCADE, related_name='test_case_results')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    
    # Results
    status = models.CharField(max_length=50, help_text="Test case result status")
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    memory_used = models.FloatField(null=True, blank=True, help_text="Memory used in MB")
    
    # Input/Output
    input_data = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    actual_output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['judge_submission', 'test_case']
        ordering = ['test_case__order']
    
    def __str__(self):
        return f"{self.judge_submission} - Test Case {self.test_case.order}"


class LanguageSupport(models.Model):
    """Model for supported programming languages."""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('c', 'C'),
        ('csharp', 'C#'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('php', 'PHP'),
        ('ruby', 'Ruby'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
    ]
    
    # Language details
    name = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    file_extension = models.CharField(max_length=10)
    judge0_id = models.IntegerField(help_text="Judge0 language ID")
    
    # Configuration
    is_active = models.BooleanField(default=True)
    time_limit_multiplier = models.FloatField(default=1.0, help_text="Time limit multiplier for this language")
    memory_limit_multiplier = models.FloatField(default=1.0, help_text="Memory limit multiplier for this language")
    
    # Template code
    template_code = models.TextField(blank=True, help_text="Default template code for this language")
    
    class Meta:
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class JudgeConfig(models.Model):
    """Model for judge configuration settings."""
    
    JUDGE_TYPE_CHOICES = [
        ('judge0', 'Judge0 API'),
        ('docker', 'Docker Sandbox'),
        ('custom', 'Custom Judge'),
    ]
    
    # Configuration
    judge_type = models.CharField(max_length=20, choices=JUDGE_TYPE_CHOICES, default='judge0')
    api_url = models.URLField(blank=True, help_text="Judge API URL")
    api_key = models.CharField(max_length=200, blank=True, help_text="API key for judge service")
    
    # Limits
    default_time_limit = models.FloatField(default=1.0, help_text="Default time limit in seconds")
    default_memory_limit = models.IntegerField(default=128, help_text="Default memory limit in MB")
    max_time_limit = models.FloatField(default=10.0, help_text="Maximum allowed time limit")
    max_memory_limit = models.IntegerField(default=512, help_text="Maximum allowed memory limit")
    
    # Settings
    enable_compilation = models.BooleanField(default=True)
    enable_runtime = models.BooleanField(default=True)
    enable_sandbox = models.BooleanField(default=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Judge Configuration'
        verbose_name_plural = 'Judge Configurations'
    
    def __str__(self):
        return f"{self.judge_type} Configuration"


class JudgeLog(models.Model):
    """Model for logging judge activities and errors."""
    
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ]
    
    # Log details
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # Related objects
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)
    judge_submission = models.ForeignKey(JudgeSubmission, on_delete=models.CASCADE, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level.upper()} - {self.message[:50]}" 