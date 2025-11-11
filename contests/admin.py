from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Contest, ContestProblem, ContestParticipation, 
    ContestSubmission, ContestLeaderboard, ContestAnnouncement
)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    """Enhanced Contest Admin with beautiful styling."""
    
    list_display = (
        'title',
        'status_badge',
        'type_badge',
        'time_display',
        'participant_count',
        'problem_count',
        'is_rated'
    )
    list_filter = ('contest_type', 'status', 'is_rated', 'start_time')
    search_fields = ('title', 'description', 'created_by__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('participants_count', 'created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('title', 'slug', 'description', 'contest_type', 'status')
        }),
        ('⏰ Timing', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('⚙️ Settings', {
            'fields': ('is_rated', 'allow_registration', 'max_participants')
        }),
        ('💰 Rewards', {
            'fields': ('total_prize_pool', 'prize_distribution')
        }),
        ('📊 Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display contest status with live indicator."""
        now = timezone.now()
        if obj.start_time > now:
            return format_html(
                '<span style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 11px;">⏳ UPCOMING</span>'
            )
        elif obj.end_time < now:
            return format_html(
                '<span style="background: #6B7280; color: white; padding: 5px 12px; border-radius: 15px; font-size: 11px;">📦 ENDED</span>'
            )
        else:
            return format_html(
                '<span style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 11px; animation: pulse 2s infinite;">🔴 LIVE</span>'
            )
    status_badge.short_description = 'Status'
    
    def type_badge(self, obj):
        """Display contest type."""
        colors = {
            'weekly': '#10B981',
            'monthly': '#3B82F6',
            'special': '#F59E0B',
            'practice': '#6B7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.contest_type, '#6B7280'),
            obj.get_contest_type_display()
        )
    type_badge.short_description = 'Type'
    
    def time_display(self, obj):
        """Display start and end times."""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div><strong>📅 Start:</strong> {}</div>'
            '<div><strong>🏁 End:</strong> {}</div>'
            '</div>',
            obj.start_time.strftime('%Y-%m-%d %H:%M'),
            obj.end_time.strftime('%Y-%m-%d %H:%M')
        )
    time_display.short_description = 'Schedule'
    
    def participant_count(self, obj):
        """Display participant count."""
        count = obj.participants_count
        return format_html(
            '<strong style="color: #667eea; font-size: 14px;">👥 {}</strong>',
            count
        )
    participant_count.short_description = 'Participants'
    
    def problem_count(self, obj):
        """Display problem count."""
        count = ContestProblem.objects.filter(contest=obj).count()
        return format_html(
            '<strong style="color: #F59E0B; font-size: 14px;">📝 {}</strong>',
            count
        )
    problem_count.short_description = 'Problems'
    
    actions = ['publish_contest', 'end_contest']
    
    def publish_contest(self, request, queryset):
        """Publish selected contests."""
        updated = queryset.update(status='published')
        self.message_user(request, f'✅ Published {updated} contests!')
    publish_contest.short_description = '✅ Publish contests'
    
    def end_contest(self, request, queryset):
        """End selected contests."""
        updated = queryset.update(status='ended')
        self.message_user(request, f'🏁 Ended {updated} contests!')
    end_contest.short_description = '🏁 End contests'


@admin.register(ContestProblem)
class ContestProblemAdmin(admin.ModelAdmin):
    """Contest Problem Admin with enhanced display."""
    
    list_display = ('contest', 'problem_link', 'order', 'points_badge', 'visibility_badge', 'difficulty_badge')
    list_filter = ('is_visible', 'contest__contest_type', 'problem__difficulty')
    search_fields = ('contest__title', 'problem__title')
    ordering = ('contest', 'order')
    list_editable = ('order',)
    
    def problem_link(self, obj):
        """Link to problem."""
        return format_html(
            '<a href="/admin/problems/problem/{}/change/" style="color: #667eea; font-weight: bold;">{}</a>',
            obj.problem.id, obj.problem.title
        )
    problem_link.short_description = 'Problem'
    
    def points_badge(self, obj):
        """Display points."""
        return format_html(
            '<span style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 5px 12px; border-radius: 10px; font-weight: bold;">⭐ {}</span>',
            obj.points
        )
    points_badge.short_description = 'Points'
    
    def visibility_badge(self, obj):
        """Display visibility."""
        if obj.is_visible:
            return format_html(
                '<span style="background: #10B981; color: white; padding: 5px 10px; border-radius: 8px; font-size: 11px; font-weight: bold;">👁️ Visible</span>'
            )
        return format_html(
            '<span style="background: #EF4444; color: white; padding: 5px 10px; border-radius: 8px; font-size: 11px; font-weight: bold;">🔒 Hidden</span>'
        )
    visibility_badge.short_description = 'Visibility'
    
    def difficulty_badge(self, obj):
        """Display difficulty."""
        colors = {
            'easy': '#10B981',
            'medium': '#F59E0B',
            'hard': '#EF4444'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.problem.difficulty, '#6B7280'),
            obj.problem.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'


@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    """Contest Participation Admin with rankings."""
    
    list_display = ('user', 'contest_link', 'score_display', 'rank_badge', 'joined_at')
    list_filter = ('contest__contest_type', 'joined_at')
    search_fields = ('user__username', 'contest__title')
    readonly_fields = ('joined_at',)
    ordering = ('contest', '-score')
    list_per_page = 50
    
    fieldsets = (
        ('👤 Participation', {
            'fields': ('contest', 'user', 'joined_at')
        }),
        ('📊 Results', {
            'fields': ('score', 'rank')
        }),
    )
    
    def contest_link(self, obj):
        """Link to contest."""
        return format_html(
            '<a href="/admin/contests/contest/{}/change/" style="color: #667eea; font-weight: bold;">{}</a>',
            obj.contest.id, obj.contest.title
        )
    contest_link.short_description = 'Contest'
    
    def score_display(self, obj):
        """Display score."""
        return format_html(
            '<strong style="color: #667eea; font-size: 14px;">🎯 {}</strong>',
            obj.score
        )
    score_display.short_description = 'Score'
    
    def rank_badge(self, obj):
        """Display rank with medal."""
        if obj.rank == 1:
            return format_html(
                '<span style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">🥇 1st</span>'
            )
        elif obj.rank == 2:
            return format_html(
                '<span style="background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">🥈 2nd</span>'
            )
        elif obj.rank == 3:
            return format_html(
                '<span style="background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">🥉 3rd</span>'
            )
        else:
            return format_html(
                '<span style="background: #E5E7EB; color: #6B7280; padding: 5px 12px; border-radius: 10px; font-weight: bold; font-size: 12px;">#{}</span>',
                obj.rank
            )
    rank_badge.short_description = 'Rank'


@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    """Contest Submission Admin."""
    
    list_display = ('participation', 'problem', 'status_badge', 'submitted_at')
    list_filter = ('status', 'submitted_at', 'problem__difficulty')
    search_fields = ('participation__user__username', 'problem__title')
    readonly_fields = ('submitted_at',)
    
    def status_badge(self, obj):
        """Display status."""
        colors = {
            'accepted': '#10B981',
            'wrong_answer': '#EF4444',
            'time_limit_exceeded': '#F59E0B',
            'runtime_error': '#DC2626'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6B7280'),
            obj.status.replace('_', ' ').upper()
        )
    status_badge.short_description = 'Status'


@admin.register(ContestLeaderboard)
class ContestLeaderboardAdmin(admin.ModelAdmin):
    """Contest Leaderboard Admin."""
    
    list_display = ('contest', 'user', 'rank_badge', 'score_display', 'problems_solved', 'last_submission')
    list_filter = ('contest__contest_type', 'rank')
    search_fields = ('contest__title', 'user__username')
    readonly_fields = ('last_submission',)
    ordering = ('contest', 'rank')
    
    def rank_badge(self, obj):
        """Display rank."""
        if obj.rank <= 3:
            medals = {1: '🥇', 2: '🥈', 3: '🥉'}
            colors = {1: '#FFD700', 2: '#C0C0C0', 3: '#CD7F32'}
            return format_html(
                '<span style="background: {}; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px;">{} #{}</span>',
                colors[obj.rank], medals[obj.rank], obj.rank
            )
        return format_html(
            '<strong style="font-size: 14px;">#{}</strong>',
            obj.rank
        )
    rank_badge.short_description = 'Rank'
    
    def score_display(self, obj):
        """Display score."""
        return format_html(
            '<strong style="color: #667eea; font-size: 14px;">🎯 {}</strong>',
            obj.score
        )
    score_display.short_description = 'Score'


@admin.register(ContestAnnouncement)
class ContestAnnouncementAdmin(admin.ModelAdmin):
    """Contest Announcement Admin."""
    
    list_display = ('contest', 'title', 'importance_badge', 'created_at')
    list_filter = ('is_important', 'created_at', 'contest__contest_type')
    search_fields = ('contest__title', 'title', 'content')
    readonly_fields = ('created_at',)
    
    def importance_badge(self, obj):
        """Display importance."""
        if obj.is_important:
            return format_html(
                '<span style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 5px 12px; border-radius: 10px; font-weight: bold; font-size: 11px;">⚠️ IMPORTANT</span>'
            )
        return format_html(
            '<span style="background: #E5E7EB; color: #6B7280; padding: 5px 10px; border-radius: 8px; font-size: 11px;">ℹ️ Normal</span>'
        )
    importance_badge.short_description = 'Priority'
