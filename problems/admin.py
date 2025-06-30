from django.contrib import admin
from .models import Problem, Tag, TestCase, Submission, ProblemDiscussion


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'problems_count')
    search_fields = ('name',)
    list_filter = ('color',)
    
    def problems_count(self, obj):
        return obj.problems.count()
    problems_count.short_description = 'Problems'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'status', 'acceptance_rate', 'total_submissions', 'created_by', 'created_at')
    list_filter = ('difficulty', 'status', 'tags', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('acceptance_rate', 'total_submissions', 'accepted_submissions', 'average_time', 'average_memory', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'difficulty', 'status')
        }),
        ('Problem Details', {
            'fields': ('constraints', 'examples', 'starter_code')
        }),
        ('Tags & Metadata', {
            'fields': ('tags', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_submissions', 'accepted_submissions', 'acceptance_rate', 
                      'average_time', 'average_memory'),
            'classes': ('collapse',)
        }),
        ('Rewards', {
            'fields': ('coin_reward', 'xp_reward')
        }),
    )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'order', 'is_hidden', 'time_limit', 'memory_limit')
    list_filter = ('is_hidden', 'problem__difficulty')
    search_fields = ('problem__title',)
    ordering = ('problem', 'order')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'status', 'execution_time', 'memory_used', 'submitted_at')
    list_filter = ('status', 'language', 'submitted_at', 'problem__difficulty')
    search_fields = ('user__username', 'problem__title', 'code')
    readonly_fields = ('submitted_at', 'judged_at', 'execution_time', 'memory_used', 
                      'test_cases_passed', 'total_test_cases')
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('user', 'problem', 'code', 'language', 'status')
        }),
        ('Results', {
            'fields': ('execution_time', 'memory_used', 'test_cases_passed', 'total_test_cases')
        }),
        ('Error Details', {
            'fields': ('error_message', 'failed_test_case'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'judged_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProblemDiscussion)
class ProblemDiscussionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'is_solution', 'vote_count', 'created_at')
    list_filter = ('is_solution', 'created_at', 'problem__difficulty')
    search_fields = ('user__username', 'problem__title', 'content')
    readonly_fields = ('vote_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Discussion', {
            'fields': ('problem', 'user', 'parent', 'content', 'is_solution')
        }),
        ('Votes', {
            'fields': ('upvotes', 'downvotes', 'vote_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 