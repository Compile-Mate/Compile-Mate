from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CoinTransaction, UserAchievement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'coins', 'xp', 'level', 'problems_solved', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'level', 'preferred_language', 'theme')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'college')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('bio', 'avatar', 'date_of_birth', 'college', 'graduation_year')
        }),
        ('MateCoins & Stats', {
            'fields': ('coins', 'xp', 'level', 'problems_solved', 'contests_participated', 
                      'current_streak', 'longest_streak', 'last_activity')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'theme')
        }),
        ('Social', {
            'fields': ('followers',)
        }),
    )
    
    readonly_fields = ('coins', 'xp', 'level', 'problems_solved', 'contests_participated', 
                      'current_streak', 'longest_streak', 'last_activity')


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'reason', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'reason')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_type', 'earned_at')
    list_filter = ('achievement_type', 'earned_at')
    search_fields = ('user__username', 'achievement_type')
    ordering = ('-earned_at',)
    readonly_fields = ('earned_at',) 