from django.contrib import admin
from .models import CertificateTemplate, Certificate, CertificateVerification, SkillAssessment, AssessmentAttempt


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'user', 'title', 'certificate_type', 'is_verified', 'issued_at']
    list_filter = ['certificate_type', 'is_verified', 'issued_at']
    search_fields = ['certificate_number', 'user__username', 'title']
    readonly_fields = ['certificate_id', 'certificate_number', 'issued_at', 'views_count']


@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = ['certificate', 'verified_by', 'verified_at']
    list_filter = ['verified_at']
    search_fields = ['certificate__certificate_number']
    readonly_fields = ['verified_at']


@admin.register(SkillAssessment)
class SkillAssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'skill', 'duration', 'passing_score', 'is_active']
    list_filter = ['skill', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'user', 'score', 'passed', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'passed', 'started_at']
    search_fields = ['assessment__name', 'user__username']
    readonly_fields = ['started_at', 'completed_at']
