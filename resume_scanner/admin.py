from django.contrib import admin
from .models import ResumeScan


@admin.register(ResumeScan)
class ResumeScanAdmin(admin.ModelAdmin):
    """Admin interface for resume scans."""
    
    list_display = ['user', 'job_field', 'ats_score', 'keyword_score', 'score_grade', 'uploaded_at']
    list_filter = ['uploaded_at', 'job_field']
    search_fields = ['user__username', 'user__email', 'job_field']
    readonly_fields = ['uploaded_at', 'ats_score', 'keyword_score', 'report', 'suggestions', 'analysis_data']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'uploaded_at', 'resume_file')
        }),
        ('Job Details', {
            'fields': ('job_field', 'job_description')
        }),
        ('Scores', {
            'fields': ('ats_score', 'keyword_score')
        }),
        ('Analysis Results', {
            'fields': ('suggestions', 'report', 'analysis_data'),
            'classes': ('collapse',)
        }),
    )
    
    def score_grade(self, obj):
        return obj.score_grade
    score_grade.short_description = 'Grade'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
