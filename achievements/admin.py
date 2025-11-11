from django.contrib import admin
from .models import (
    BadgeCategory, Badge, UserBadge, Achievement, UserAchievement,
    BadgeProgress, Milestone, UserMilestone
)


@admin.register(BadgeCategory)
class BadgeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'display_order']
    list_editable = ['display_order']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'badge_type', 'requirement_type', 'requirement_value', 'coin_reward', 'xp_reward', 'is_active']
    list_filter = ['tier', 'badge_type', 'is_active', 'is_secret']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at', 'is_displayed', 'is_new']
    list_filter = ['earned_at', 'is_displayed', 'is_new', 'badge__tier']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['earned_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'coin_reward', 'xp_reward', 'is_repeatable', 'is_active']
    list_filter = ['achievement_type', 'is_repeatable', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'completion_count', 'completed_at']
    list_filter = ['completed_at', 'achievement__achievement_type']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ['completed_at']


@admin.register(BadgeProgress)
class BadgeProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'current_value', 'target_value', 'progress_percentage', 'is_complete', 'last_updated']
    list_filter = ['last_updated', 'badge__badge_type']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['last_updated']
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.1f}%"
    progress_percentage.short_description = 'Progress'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'milestone_type', 'threshold', 'coin_reward', 'xp_reward', 'is_active']
    list_filter = ['milestone_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserMilestone)
class UserMilestoneAdmin(admin.ModelAdmin):
    list_display = ['user', 'milestone', 'value_achieved', 'achieved_at']
    list_filter = ['achieved_at', 'milestone__milestone_type']
    search_fields = ['user__username', 'milestone__name']
    readonly_fields = ['achieved_at']
