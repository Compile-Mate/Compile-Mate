from django.contrib import admin
from .models import Notification, SiteSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Content', {
            'fields': ('related_url', 'related_object_id', 'related_object_type'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'maintenance_mode', 'enable_registration', 'enable_contests')
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'site_logo')
        }),
        ('Features', {
            'fields': ('enable_registration', 'enable_social_login', 'enable_contests', 'enable_rewards')
        }),
        ('MateCoins Settings', {
            'fields': ('initial_coins', 'coins_per_accepted_solution', 'coins_per_hard_problem', 
                      'coins_per_contest_participation', 'coins_per_weekly_streak')
        }),
        ('Contest Settings', {
            'fields': ('default_contest_duration', 'max_contest_problems')
        }),
        ('Judge Settings', {
            'fields': ('default_time_limit', 'default_memory_limit')
        }),
        ('Social Features', {
            'fields': ('enable_following', 'enable_discussions', 'enable_achievements')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one site settings instance
        return not SiteSettings.objects.exists() 