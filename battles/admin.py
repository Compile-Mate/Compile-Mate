from django.contrib import admin
from .models import Battle, BattleSubmission, BattleInvitation, BattleStats


@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display = ['battle_id', 'challenger', 'opponent', 'problem', 'status', 'stake', 'winner', 'created_at']
    list_filter = ['status', 'mode', 'created_at']
    search_fields = ['challenger__username', 'opponent__username', 'battle_id']
    readonly_fields = ['battle_id', 'created_at', 'started_at', 'ended_at', 'spectator_count']
    filter_horizontal = ['spectators']


@admin.register(BattleSubmission)
class BattleSubmissionAdmin(admin.ModelAdmin):
    list_display = ['battle', 'user', 'submission', 'submitted_at', 'time_taken']
    list_filter = ['submitted_at']
    search_fields = ['user__username', 'battle__battle_id']
    readonly_fields = ['submitted_at', 'time_taken']


@admin.register(BattleInvitation)
class BattleInvitationAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'problem', 'stake', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at']


@admin.register(BattleStats)
class BattleStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_battles', 'battles_won', 'battles_lost', 'win_rate', 'win_streak', 'best_win_streak']
    search_fields = ['user__username']
    readonly_fields = ['total_battles', 'battles_won', 'battles_lost', 'total_coins_won', 'total_coins_lost']
    
    def win_rate(self, obj):
        return f"{obj.win_rate:.1f}%"
    win_rate.short_description = 'Win Rate'
