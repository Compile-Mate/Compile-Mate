"""
Judge App Admin Configuration
"""

from django.contrib import admin
from .models import (
    JudgeSubmission,
    TestCaseResult,
    LanguageSupport,
    JudgeConfig,
    JudgeLog
)


@admin.register(JudgeSubmission)
class JudgeSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'judge_id', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['judge_id', 'submission__user__username', 'submission__problem__title']
    readonly_fields = ['created_at', 'processed_at']
    date_hierarchy = 'created_at'


@admin.register(TestCaseResult)
class TestCaseResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'judge_submission', 'test_case', 'status', 'execution_time']
    list_filter = ['status']
    search_fields = ['judge_submission__judge_id']


@admin.register(LanguageSupport)
class LanguageSupportAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'display_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']


@admin.register(JudgeConfig)
class JudgeConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'judge_type', 'is_active', 'updated_at']
    list_filter = ['judge_type', 'is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JudgeLog)
class JudgeLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'judge_submission', 'level', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['judge_submission__judge_id', 'message']
    date_hierarchy = 'created_at'
