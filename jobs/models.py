from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from problems.models import Problem


class Company(models.Model):
    """Model for companies posting jobs."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    website = models.URLField()
    logo_url = models.URLField(blank=True)
    
    # Contact
    recruiter_email = models.EmailField()
    recruiter_name = models.CharField(max_length=200)
    
    # Social
    linkedin_url = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JobPosting(models.Model):
    """Model for job postings."""
    
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]
    
    # Basic information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    
    # Job details
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    location = models.CharField(max_length=200)
    remote_ok = models.BooleanField(default=False)
    
    # Requirements
    required_skills = models.JSONField(default=list, help_text="List of required skills")
    min_experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Compensation
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Coding challenge
    has_challenge = models.BooleanField(default=True)
    challenge_problems = models.ManyToManyField(Problem, related_name='job_challenges', blank=True)
    challenge_duration = models.IntegerField(default=60, help_text="Duration in minutes")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    applications_count = models.IntegerField(default=0)
    
    # Metadata
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posted_jobs')
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['status', '-posted_at']),
            models.Index(fields=['company', '-posted_at']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobApplication(models.Model):
    """Model for job applications."""
    
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('challenge_sent', 'Challenge Sent'),
        ('challenge_completed', 'Challenge Completed'),
        ('interview', 'Interview'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application materials
    cover_letter = models.TextField(blank=True)
    resume_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    
    # Challenge results
    challenge_score = models.IntegerField(null=True, blank=True, help_text="Percentage score")
    challenge_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Recruiter notes
    recruiter_notes = models.TextField(blank=True)
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['applicant', '-applied_at']),
            models.Index(fields=['job', 'status', '-applied_at']),
        ]
    
    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} ({self.status})"


class CodingChallenge(models.Model):
    """Model for job-specific coding challenges."""
    
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='coding_challenge')
    problems = models.ManyToManyField(Problem, related_name='job_challenge_attempts')
    
    started_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    total_problems = models.IntegerField()
    solved_problems = models.IntegerField(default=0)
    score = models.IntegerField(default=0, help_text="Percentage score")
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Challenge for {self.application.applicant.username} - {self.application.job.title}"


class RecruiterProfile(models.Model):
    """Model for recruiter profiles."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='recruiters')
    title = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['company', 'user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name}"
