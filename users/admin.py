from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, CoinTransaction, UserAchievement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'stats_display', 'level_badge', 'streak_badge', 'role_badge')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'level', 'preferred_language', 'theme')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'college')
    ordering = ('-date_joined',)
    list_per_page = 30
    
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
    
    actions = ['give_bonus_coins', 'reset_streak', 'level_up_users']
    
    def stats_display(self, obj):
        """Display user stats."""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div>💰 <strong>{}</strong> coins</div>'
            '<div>⚡ <strong>{}</strong> XP</div>'
            '<div>✅ <strong>{}</strong> solved</div>'
            '</div>',
            obj.coins, obj.xp, obj.problems_solved
        )
    stats_display.short_description = 'Stats'
    
    def level_badge(self, obj):
        """Display user level."""
        colors = ['#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#EF4444']
        color = colors[min(obj.level // 5, len(colors) - 1)]
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;">🏆 Level {}</span>',
            color, obj.level
        )
    level_badge.short_description = 'Level'
    
    def streak_badge(self, obj):
        """Display streak."""
        if obj.current_streak > 0:
            return format_html(
                '<span style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 11px;">🔥 {} days</span>',
                obj.current_streak
            )
        return format_html('<span style="color: #9CA3AF; font-size: 11px;">No streak</span>')
    streak_badge.short_description = 'Streak'
    
    def role_badge(self, obj):
        """Display role."""
        if obj.is_superuser:
            return format_html(
                '<span style="background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">👑 ADMIN</span>'
            )
        elif obj.is_staff:
            return format_html(
                '<span style="background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%); color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">⭐ STAFF</span>'
            )
        return format_html(
            '<span style="background: #E5E7EB; color: #6B7280; padding: 5px 10px; border-radius: 10px; font-size: 11px;">👤 User</span>'
        )
    role_badge.short_description = 'Role'
    
    def give_bonus_coins(self, request, queryset):
        """Give 100 bonus coins."""
        for user in queryset:
            user.coins += 100
            user.save()
        self.message_user(request, f'💰 Gave 100 coins to {queryset.count()} users!')
    give_bonus_coins.short_description = '💰 Give 100 bonus coins'
    
    def reset_streak(self, request, queryset):
        """Reset streak."""
        queryset.update(current_streak=0)
        self.message_user(request, f'🔥 Reset streak for {queryset.count()} users.')
    reset_streak.short_description = '🔥 Reset streak'
    
    def level_up_users(self, request, queryset):
        """Level up users."""
        for user in queryset:
            user.level += 1
            user.save()
        self.message_user(request, f'🚀 Leveled up {queryset.count()} users!')
    level_up_users.short_description = '🚀 Level up users'


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_badge', 'amount_display', 'reason', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'reason')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    list_per_page = 50
    
    def type_badge(self, obj):
        """Display transaction type."""
        colors = {
            'earn': '#10B981',
            'spend': '#EF4444',
            'bonus': '#F59E0B',
            'refund': '#3B82F6'
        }
        icons = {
            'earn': '💵',
            'spend': '💸',
            'bonus': '🎁',
            'refund': '↩️'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            colors.get(obj.transaction_type, '#6B7280'),
            icons.get(obj.transaction_type, '💰'),
            obj.get_transaction_type_display()
        )
    type_badge.short_description = 'Type'
    
    def amount_display(self, obj):
        """Display amount with color."""
        if obj.transaction_type in ['earn', 'bonus', 'refund']:
            color = '#10B981'
            sign = '+'
        else:
            color = '#EF4444'
            sign = '-'
        return format_html(
            '<strong style="color: {}; font-size: 14px;">{}{}</strong>',
            color, sign, obj.amount
        )
    amount_display.short_description = 'Amount'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_badge', 'earned_at')
    list_filter = ('achievement_type', 'earned_at')
    search_fields = ('user__username', 'achievement_type')
    ordering = ('-earned_at',)
    readonly_fields = ('earned_at',)
    list_per_page = 50
    
    def achievement_badge(self, obj):
        """Display achievement with icon."""
        icons = {
            'first_solve': '🎯',
            'streak_7': '🔥',
            'streak_30': '🔥🔥',
            'streak_100': '🔥🔥🔥',
            'contest_winner': '🏆',
            'speedster': '⚡',
            'problem_setter': '📝'
        }
        return format_html(
            '<span style="background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">{} {}</span>',
            icons.get(obj.achievement_type, '🏅'),
            obj.get_achievement_type_display()
        )
    achievement_badge.short_description = 'Achievement' 