from django.db import models
from users.models import User

class ResumeScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_scans')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    resume_file = models.FileField(upload_to='resumes/')
    job_field = models.CharField(max_length=100, blank=True)
    job_description = models.TextField(blank=True)
    ats_score = models.FloatField(default=0.0)
    keyword_score = models.FloatField(default=0.0)
    suggestions = models.JSONField(default=list, blank=True)
    report = models.TextField(blank=True)

    def __str__(self):
        return f"ResumeScan({self.user.username}, {self.uploaded_at})"
