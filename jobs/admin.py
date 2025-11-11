from django.contrib import admin
from .models import Company, JobPosting, JobApplication, CodingChallenge, RecruiterProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'experience_level', 'status', 'applications_count', 'posted_at']
    list_filter = ['job_type', 'experience_level', 'status', 'remote_ok', 'posted_at']
    search_fields = ['title', 'company__name', 'description']
    readonly_fields = ['applications_count', 'posted_at']
    filter_horizontal = ['challenge_problems']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'status', 'challenge_score', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['job__title', 'applicant__username']
    readonly_fields = ['applied_at', 'updated_at']


@admin.register(CodingChallenge)
class CodingChallengeAdmin(admin.ModelAdmin):
    list_display = ['application', 'total_problems', 'solved_problems', 'score', 'started_at', 'completed_at']
    list_filter = ['started_at', 'completed_at']
    search_fields = ['application__applicant__username', 'application__job__title']
    filter_horizontal = ['problems']


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'title', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at', 'company']
    search_fields = ['user__username', 'company__name']
