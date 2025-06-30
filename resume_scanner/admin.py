from django.contrib import admin
from .models import ResumeScan

@admin.register(ResumeScan)
class ResumeScanAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'ats_score', 'keyword_score')
    search_fields = ('user__username', 'job_field')
    readonly_fields = ('uploaded_at', 'ats_score', 'keyword_score', 'suggestions', 'report')
