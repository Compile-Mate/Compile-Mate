from django.db import models
from users.models import User


class ResumeScan(models.Model):
    """Model for storing resume analysis results."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_scans')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    resume_file = models.FileField(upload_to='resumes/')
    job_field = models.CharField(max_length=100, blank=True)
    job_description = models.TextField(blank=True)
    
    # Scores
    ats_score = models.FloatField(default=0.0, help_text="ATS compatibility score")
    keyword_score = models.FloatField(default=0.0, help_text="Keyword match score")
    
    # Results
    suggestions = models.JSONField(default=list, blank=True, help_text="Improvement suggestions")
    report = models.TextField(blank=True, help_text="Detailed analysis report")
    analysis_data = models.JSONField(default=dict, blank=True, help_text="Complete analysis data")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Resume Scan'
        verbose_name_plural = 'Resume Scans'
    
    def __str__(self):
        return f"{self.user.username} - {self.job_field} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    @property
    def score_color(self):
        """Get color based on score."""
        score = self.ats_score
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellow'
        else:
            return 'red'
    
    @property
    def score_grade(self):
        """Get letter grade based on score."""
        score = self.ats_score
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
