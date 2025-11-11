from django.contrib import admin
from .models import Notification, SiteSettings, UserActivity, FAQ, ContactMessage, SystemLog, SupportChat, ChatMessage, AdminAvailability, ChatTemplate, ChatRating


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


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    ordering = ['category', 'order']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_closed']

    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = "Mark selected messages as replied"

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Mark selected messages as closed"


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'user', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'user__username']
    readonly_fields = ['created_at']


# Support Chat Admin
@admin.register(SupportChat)
class SupportChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'priority', 'category', 'admin', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['user__username', 'subject', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_activity', 'duration']
    list_select_related = ['user', 'admin']
    
    fieldsets = (
        ('Chat Information', {
            'fields': ('user', 'admin', 'subject', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'category', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('user_agent', 'ip_address', 'page_url'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_admin', 'mark_as_resolved', 'mark_as_closed']
    
    def assign_to_admin(self, request, queryset):
        # Auto-assign to current admin user
        for chat in queryset:
            if not chat.admin:
                chat.admin = request.user
                chat.status = 'in_progress'
                chat.save()
    assign_to_admin.short_description = "Assign selected chats to current admin"
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
    mark_as_resolved.short_description = "Mark selected chats as resolved"
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Mark selected chats as closed"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'sender', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['chat__subject', 'sender__username', 'content']
    readonly_fields = ['created_at', 'edited_at']
    list_select_related = ['chat', 'sender']


@admin.register(AdminAvailability)
class AdminAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['admin', 'is_online', 'is_available', 'current_chats', 'max_concurrent_chats', 'avg_response_time']
    list_filter = ['is_online', 'is_available']
    search_fields = ['admin__username']
    readonly_fields = ['last_activity', 'avg_response_time', 'satisfaction_rating', 'chats_resolved']


@admin.register(ChatTemplate)
class ChatTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'usage_count']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'subject', 'content']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(ChatRating)
class ChatRatingAdmin(admin.ModelAdmin):
    list_display = ['chat', 'user', 'overall_rating', 'response_time_rating', 'helpfulness_rating', 'created_at']
    list_filter = ['overall_rating', 'response_time_rating', 'helpfulness_rating', 'created_at']
    search_fields = ['chat__subject', 'user__username', 'feedback']
    readonly_fields = ['created_at']
    list_select_related = ['chat', 'user'] 