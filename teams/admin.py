from django.contrib import admin
from .models import Team, TeamMembership, TeamInvitation, TeamContest, TeamAchievement


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'founder', 'member_count', 'total_xp', 'rank', 'is_public', 'is_recruiting']
    list_filter = ['is_public', 'is_recruiting', 'created_at']
    search_fields = ['name', 'founder__username']
    readonly_fields = ['team_id', 'total_coins', 'total_xp', 'problems_solved', 'created_at']
    filter_horizontal = ['leaders', 'members']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'role', 'contribution_score', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['team__name', 'user__username']


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ['team', 'from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['team__name', 'from_user__username', 'to_user__username']


@admin.register(TeamContest)
class TeamContestAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'prize_pool']
    list_filter = ['start_time']
    search_fields = ['name']
    filter_horizontal = ['participating_teams', 'problems']


@admin.register(TeamAchievement)
class TeamAchievementAdmin(admin.ModelAdmin):
    list_display = ['team', 'name', 'earned_at']
    list_filter = ['earned_at']
    search_fields = ['team__name', 'name']
