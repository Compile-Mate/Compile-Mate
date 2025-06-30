from django.contrib import admin
from .models import (
    Contest, ContestProblem, ContestParticipation, 
    ContestSubmission, ContestLeaderboard, ContestAnnouncement
)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'contest_type', 'status', 'start_time', 'end_time', 'participants_count', 'is_rated')
    list_filter = ('contest_type', 'status', 'is_rated', 'start_time')
    search_fields = ('title', 'description', 'created_by__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('participants_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'contest_type', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Settings', {
            'fields': ('is_rated', 'allow_registration', 'max_participants')
        }),
        ('Rewards', {
            'fields': ('total_prize_pool', 'prize_distribution')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContestProblem)
class ContestProblemAdmin(admin.ModelAdmin):
    list_display = ('contest', 'problem', 'order', 'points', 'is_visible')
    list_filter = ('is_visible', 'contest__contest_type', 'problem__difficulty')
    search_fields = ('contest__title', 'problem__title')
    ordering = ('contest', 'order')


@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'score', 'rank', 'joined_at')
    list_filter = ('contest__contest_type', 'joined_at')
    search_fields = ('user__username', 'contest__title')
    readonly_fields = ('joined_at',)
    
    fieldsets = (
        ('Participation', {
            'fields': ('contest', 'user', 'joined_at')
        }),
        ('Results', {
            'fields': ('score', 'rank')
        }),
    )


@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    list_display = ('participation', 'problem', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at', 'problem__difficulty')
    search_fields = ('participation__user__username', 'problem__title')
    readonly_fields = ('submitted_at',)


@admin.register(ContestLeaderboard)
class ContestLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('contest', 'user', 'rank', 'score', 'problems_solved')
    list_filter = ('contest__contest_type', 'rank')
    search_fields = ('contest__title', 'user__username')
    readonly_fields = ('last_submission',)


@admin.register(ContestAnnouncement)
class ContestAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('contest', 'title', 'is_important', 'created_at')
    list_filter = ('is_important', 'created_at', 'contest__contest_type')
    search_fields = ('contest__title', 'title', 'content')
    readonly_fields = ('created_at',) 