from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Problem, TestCase, Tag, Submission, ProblemDiscussion
import json


class TestCaseInline(admin.TabularInline):
    """Inline test case editor."""
    model = TestCase
    extra = 2
    fields = ('order', 'input_data', 'expected_output', 'is_hidden', 'time_limit', 'memory_limit')
    classes = ('collapse',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Enhanced Tag admin."""
    list_display = ('name', 'colored_tag', 'problem_count', 'description')
    search_fields = ('name', 'description')
    list_per_page = 50
    
    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            obj.color, obj.name
        )
    colored_tag.short_description = 'Tag Preview'
    
    def problem_count(self, obj):
        count = obj.problems.count()
        return format_html('<strong>{}</strong> problems', count)
    problem_count.short_description = 'Problems'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    """Super Advanced Problem Admin Interface."""
    
    # List display
    list_display = (
        'id',
        'colored_title',
        'difficulty_badge',
        'status_badge',
        'stats_display',
        'rewards_display',
        'created_by',
        'created_at',
    )
    
    # Filters
    list_filter = (
        'difficulty',
        'status',
        'created_at',
        'tags',
    )
    
    # Search
    search_fields = ('title', 'description', 'slug')
    
    # Ordering
    ordering = ('-created_at',)
    
    # Items per page
    list_per_page = 25
    
    # Fieldsets for organized form
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('title', 'slug', 'difficulty', 'status')
        }),
        ('📝 Problem Description', {
            'fields': ('description',),
            'classes': ('wide',),
            'description': 'Write the problem description, examples, input/output format.'
        }),
        ('⚠️ Constraints', {
            'fields': ('constraints',),
            'classes': ('wide',),
            'description': 'Add constraints (one per line). Example: 2 ≤ n ≤ 10⁴'
        }),
        ('💻 Starter Code', {
            'fields': ('starter_code',),
            'classes': ('collapse',),
            'description': 'Provide starter code for different languages as JSON.'
        }),
        ('🏷️ Classification', {
            'fields': ('tags',),
            'classes': ('wide',)
        }),
        ('🎁 Rewards & Metadata', {
            'fields': ('coin_reward', 'xp_reward', 'created_by'),
            'classes': ('wide',)
        }),
    )
    
    # Inlines
    inlines = [TestCaseInline]
    
    # Filters on the side
    filter_horizontal = ('tags',)
    
    # Prepopulate slug from title
    prepopulated_fields = {'slug': ('title',)}
    
    # Read-only fields
    readonly_fields = ('acceptance_rate', 'average_time', 'average_memory')
    
    # Actions
    actions = ['publish_problems', 'archive_problems', 'duplicate_problem']
    
    def colored_title(self, obj):
        """Display title with icon."""
        return format_html(
            '<div style="font-weight: bold; font-size: 14px;">📌 {}</div>',
            obj.title
        )
    colored_title.short_description = 'Problem Title'
    
    def difficulty_badge(self, obj):
        """Display difficulty with color badge."""
        colors = {
            'easy': '#10B981',
            'medium': '#F59E0B',
            'hard': '#EF4444'
        }
        icons = {
            'easy': '🟢',
            'medium': '🟡',
            'hard': '🔴'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;">{} {}</span>',
            colors.get(obj.difficulty, '#6B7280'),
            icons.get(obj.difficulty, '⚪'),
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def status_badge(self, obj):
        """Display status with badge."""
        colors = {
            'draft': '#6B7280',
            'published': '#10B981',
            'archived': '#EF4444'
        }
        icons = {
            'draft': '📝',
            'published': '✅',
            'archived': '📦'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 12px; border-radius: 15px; font-size: 11px;">{} {}</span>',
            colors.get(obj.status, '#6B7280'),
            icons.get(obj.status, '📄'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def stats_display(self, obj):
        """Display statistics."""
        if obj.total_submissions > 0:
            return format_html(
                '<div style="font-size: 12px;">'
                '<div>📊 <strong>{}</strong> submissions</div>'
                '<div>✅ <strong>{}</strong> accepted</div>'
                '<div>📈 <strong>{:.1f}%</strong> acceptance</div>'
                '</div>',
                obj.total_submissions,
                obj.accepted_submissions,
                obj.acceptance_rate
            )
        return format_html('<span style="color: #9CA3AF;">No submissions yet</span>')
    stats_display.short_description = 'Statistics'
    
    def rewards_display(self, obj):
        """Display rewards."""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div>💰 <strong>{}</strong> coins</div>'
            '<div>⚡ <strong>{}</strong> XP</div>'
            '</div>',
            obj.coin_reward,
            obj.xp_reward
        )
    rewards_display.short_description = 'Rewards'
    
    def publish_problems(self, request, queryset):
        """Bulk publish problems."""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} problems published successfully! ✅')
    publish_problems.short_description = '✅ Publish selected problems'
    
    def archive_problems(self, request, queryset):
        """Bulk archive problems."""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} problems archived. 📦')
    archive_problems.short_description = '📦 Archive selected problems'
    
    def duplicate_problem(self, request, queryset):
        """Duplicate selected problems."""
        count = 0
        for problem in queryset:
            problem.pk = None
            problem.title = f"{problem.title} (Copy)"
            problem.slug = f"{problem.slug}-copy-{count}"
            problem.status = 'draft'
            problem.save()
            count += 1
        self.message_user(request, f'{count} problems duplicated! 📋')
    duplicate_problem.short_description = '📋 Duplicate selected problems'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    """Test case admin."""
    list_display = ('problem', 'order', 'is_hidden', 'time_limit', 'memory_limit')
    list_filter = ('is_hidden', 'problem__difficulty')
    search_fields = ('problem__title',)
    list_editable = ('order', 'is_hidden')
    ordering = ('problem', 'order')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Enhanced Submission admin."""
    list_display = (
        'id',
        'user',
        'problem_link',
        'status_badge',
        'language',
        'test_cases_display',
        'execution_stats',
        'submitted_at'
    )
    list_filter = ('status', 'language', 'submitted_at')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('user', 'problem', 'code', 'status', 'error_message', 'execution_time', 'memory_used', 'submitted_at', 'judged_at')
    list_per_page = 50
    
    def problem_link(self, obj):
        return format_html('<a href="/admin/problems/problem/{}/change/">{}</a>', obj.problem.id, obj.problem.title)
    problem_link.short_description = 'Problem'
    
    def status_badge(self, obj):
        colors = {
            'accepted': '#10B981',
            'wrong_answer': '#EF4444',
            'time_limit_exceeded': '#F59E0B',
            'memory_limit_exceeded': '#F59E0B',
            'runtime_error': '#DC2626',
            'compilation_error': '#7C3AED',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6B7280'),
            obj.status.replace('_', ' ').upper()
        )
    status_badge.short_description = 'Status'
    
    def test_cases_display(self, obj):
        """Display test cases passed."""
        if obj.total_test_cases > 0:
            percentage = (obj.test_cases_passed / obj.total_test_cases) * 100
            color = '#10B981' if percentage == 100 else '#F59E0B' if percentage > 50 else '#EF4444'
            return format_html(
                '<div style="font-size: 12px;">'
                '<strong style="color: {};">{}/{}</strong>'
                '<div style="color: #6B7280; font-size: 10px;">({:.0f}%)</div>'
                '</div>',
                color, obj.test_cases_passed, obj.total_test_cases, percentage
            )
        return format_html('<span style="color: #9CA3AF;">-</span>')
    test_cases_display.short_description = 'Test Cases'
    
    def execution_stats(self, obj):
        if obj.execution_time or obj.memory_used:
            return format_html(
                '<div style="font-size: 11px;">'
                '<div>⏱️ {:.2f}s</div>'
                '<div>💾 {:.1f}MB</div>'
                '</div>',
                obj.execution_time or 0,
                obj.memory_used or 0
            )
        return '-'
    execution_stats.short_description = 'Stats'


@admin.register(ProblemDiscussion)
class ProblemDiscussionAdmin(admin.ModelAdmin):
    """Problem Discussion admin."""
    list_display = ('problem', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'problem__title')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        """Display content preview."""
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html(
            '<div style="max-width: 400px; font-size: 12px;">{}</div>',
            preview
        )
    content_preview.short_description = 'Content'


# Customize admin site headers
admin.site.site_header = "🚀 CompileMate Admin Dashboard"
admin.site.site_title = "CompileMate Admin"
admin.site.index_title = "Welcome to CompileMate Advanced Admin Panel 💻"
