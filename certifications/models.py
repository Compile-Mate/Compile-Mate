from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from learning_paths.models import LearningPath
import uuid


class CertificateTemplate(models.Model):
    """Model for certificate templates."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Design
    template_html = models.TextField(help_text="HTML template for certificate")
    background_image_url = models.URLField(blank=True)
    
    # Customization
    primary_color = models.CharField(max_length=7, default='#3B82F6')
    secondary_color = models.CharField(max_length=7, default='#10B981')
    font_family = models.CharField(max_length=100, default='Arial')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    """Model for certification types (blueprint for certificates)."""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Requirements
    learning_path = models.ForeignKey(LearningPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='certifications')
    required_problems_solved = models.IntegerField(default=0)
    required_contests_participated = models.IntegerField(default=0)
    
    # Badge
    badge_icon = models.CharField(max_length=50, default='🏆')
    badge_color = models.CharField(max_length=7, default='#3B82F6')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['difficulty_level', 'name']
    
    def __str__(self):
        return self.name


class UserCertification(models.Model):
    """Model for user's earned certifications."""
    
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='user_certifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_certifications')
    
    # Identification
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Timing
    earned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=True)
    blockchain_hash = models.CharField(max_length=200, blank=True)
    
    # Social
    shared_on_linkedin = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['certification', 'user']
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', '-earned_at']),
            models.Index(fields=['certificate_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.certification.name}"
    
    @property
    def is_valid(self):
        """Check if certificate is still valid."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() < self.expires_at
        return True


class Certificate(models.Model):
    """Legacy model - kept for backward compatibility."""
    
    CERTIFICATE_TYPE_CHOICES = [
        ('path_completion', 'Learning Path Completion'),
        ('contest_winner', 'Contest Winner'),
        ('achievement', 'Special Achievement'),
        ('skill_mastery', 'Skill Mastery'),
    ]
    
    # Identification
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    
    # Certificate details
    certificate_type = models.CharField(max_length=30, choices=CERTIFICATE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Related content
    learning_path = models.ForeignKey(LearningPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    
    # Design
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Verification
    verification_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=True)
    
    # Blockchain (optional)
    blockchain_hash = models.CharField(max_length=200, blank=True, help_text="Blockchain verification hash")
    
    # PDF
    pdf_url = models.URLField(blank=True, help_text="URL to generated PDF")
    
    # Metadata
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Some certificates may expire")
    
    # Social sharing
    shared_on_linkedin = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['user', '-issued_at']),
            models.Index(fields=['certificate_id']),
        ]
    
    def __str__(self):
        return f"Certificate: {self.title} - {self.user.username}"
    
    @property
    def is_valid(self):
        """Check if certificate is still valid."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() < self.expires_at
        return True


class CertificateVerification(models.Model):
    """Model for tracking certificate verifications."""
    
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verifications')
    verified_by = models.GenericIPAddressField(help_text="IP address of verifier")
    verified_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-verified_at']
    
    def __str__(self):
        return f"Verification of {self.certificate.certificate_number} at {self.verified_at}"


class SkillAssessment(models.Model):
    """Model for skill assessments."""
    
    SKILL_CHOICES = [
        ('algorithms', 'Algorithms'),
        ('data_structures', 'Data Structures'),
        ('dynamic_programming', 'Dynamic Programming'),
        ('graphs', 'Graph Theory'),
        ('trees', 'Trees'),
        ('arrays', 'Arrays & Strings'),
        ('system_design', 'System Design'),
    ]
    
    name = models.CharField(max_length=200)
    skill = models.CharField(max_length=50, choices=SKILL_CHOICES)
    description = models.TextField()
    
    # Assessment details
    duration = models.IntegerField(help_text="Duration in minutes")
    passing_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Questions/Problems
    assessment_data = models.JSONField(help_text="Assessment questions and problems")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['skill', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.skill})"


class AssessmentAttempt(models.Model):
    """Model for skill assessment attempts."""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    passed = models.BooleanField(default=False)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    results_data = models.JSONField(default=dict, help_text="Detailed results")
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.name}: {self.score}%"
