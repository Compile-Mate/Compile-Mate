from re import template
from statistics import mode
from unicodedata import name
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator, RegexValidator
from django.core.exceptions import ValidationError

class User(models.Model):
    username = models.CharField(
        primary_key=True,
        max_length=122,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(122),
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores'
            )
        ]
    )
    name = models.CharField(max_length=122)
    email = models.CharField(
        unique=True,
        max_length=122,
        validators=[EmailValidator()]
    )
    password = models.CharField(
        max_length=32,
        validators=[MinLengthValidator(8)]
    )
    problems_solved = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ]
    
    TYPE_CHOICES = [
        ('Array', 'Array'),
        ('String', 'String'),
        ('Tree', 'Tree'),
        ('Graph', 'Graph'),
        ('Dynamic Programming', 'Dynamic Programming'),
        ('Greedy', 'Greedy'),
        ('Backtracking', 'Backtracking'),
        ('Other', 'Other')
    ]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=122)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    difficuilty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    statement = models.TextField()
    task = models.TextField(null=True, blank=True)
    time_complexity = models.CharField(max_length=50, null=True, blank=True)
    space_complexity = models.CharField(max_length=50, null=True, blank=True)
    constraints = models.TextField(
        null=True, 
        blank=True,
        help_text="Enter each constraint on a new line"
    )
    example = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.constraints:
            # Clean up constraints before saving
            constraints_list = [c.strip() for c in self.constraints.split('\n') if c.strip()]
            self.constraints = '\n'.join(constraints_list)
        super().save(*args, **kwargs)

    def get_constraints(self):
        """Helper method to get constraints as a list"""
        if not self.constraints:
            return []
        return [c.strip() for c in self.constraints.split('\n') if c.strip()]

    def __str__(self) -> str:
        return self.name

class ProblemSolution(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='solution')
    python_solution = models.TextField(null=True, blank=True)
    cpp_solution = models.TextField(null=True, blank=True)
    java_solution = models.TextField(null=True, blank=True)
    function_name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z_][a-zA-Z0-9_]*$',
                message='Function name must be a valid identifier'
            )
        ]
    )
    python_template = models.TextField(null=True, blank=True)
    cpp_template = models.TextField(null=True, blank=True)
    java_template = models.TextField(null=True, blank=True)

    def get_solution(self, language):
        if language == 'python':
            return self.python_solution
        elif language == 'cpp':
            return self.cpp_solution
        elif language == 'java':
            return self.java_solution
        return None

    def get_template(self, language):
        if language == 'python':
            return self.python_template
        elif language == 'cpp':
            return self.cpp_template
        elif language == 'java':
            return self.java_template
        return None

class Contest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(Problem, related_name='contests')
    participants = models.ManyToManyField(User, related_name='participated_contests', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

class Submission(models.Model):
    VERDICT_CHOICES = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('RE', 'Runtime Error'),
        ('CE', 'Compilation Error'),
        ('PE', 'Presentation Error')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField(null=True)
    verdict = models.CharField(max_length=255, choices=VERDICT_CHOICES)
    time = models.DateTimeField(auto_now_add=True)

class TestCases(models.Model):
    input = models.TextField()
    output = models.TextField()
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases_set', null=True, blank=True)

    def __str__(self):
        return f"Test case for {self.problem.name if self.problem else 'Unknown Problem'}"

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Test case for {self.problem.name}"

class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('submission', 'Submission'),
        ('achievement', 'Achievement'),
        ('other', 'Other')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-time']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f"{self.user.name} - {self.title}"
