from django.contrib import admin
from .models import (
    DailyChallenge, DailyChallengeParticipation, StreakStats,
    StreakFreezeItem, StreakFreezePurchase, DailyChallengeLeaderboard
)


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['date', 'problem', 'bonus_coins', 'bonus_xp', 'participants_count', 'completed_count', 'completion_rate']
    list_filter = ['date']
    search_fields = ['problem__title']
    readonly_fields = ['participants_count', 'completed_count', 'created_at']
    
    def completion_rate(self, obj):
        return f"{obj.completion_rate:.1f}%"
    completion_rate.short_description = 'Completion Rate'


@admin.register(DailyChallengeParticipation)
class DailyChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'status', 'started_at', 'completed_at', 'time_taken', 'coins_earned']
    list_filter = ['status', 'started_at']
    search_fields = ['user__username', 'challenge__date']
    readonly_fields = ['started_at', 'completed_at', 'time_taken', 'coins_earned', 'xp_earned']


@admin.register(StreakStats)
class StreakStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_challenges_completed', 'last_completed_date', 'streak_freeze_count']
    search_fields = ['user__username']
    readonly_fields = ['total_challenges_completed']


@admin.register(StreakFreezeItem)
class StreakFreezeItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost_in_coins', 'icon', 'is_available']
    list_filter = ['is_available']


@admin.register(StreakFreezePurchase)
class StreakFreezePurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'quantity', 'total_cost', 'purchased_at']
    list_filter = ['purchased_at']
    search_fields = ['user__username']
    readonly_fields = ['total_cost', 'purchased_at']


@admin.register(DailyChallengeLeaderboard)
class DailyChallengeLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'rank', 'user', 'time_taken', 'completed_at']
    list_filter = ['challenge__date']
    search_fields = ['user__username', 'challenge__date']
    readonly_fields = ['rank', 'completed_at']
