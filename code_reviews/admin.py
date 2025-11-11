from django.contrib import admin
from .models import CodeReviewRequest, CodeReview, CodeReviewComment, ReviewerRating, ReviewerStats


@admin.register(CodeReviewRequest)
class CodeReviewRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'requester', 'reviewer', 'status', 'priority', 'coin_offer', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'requester__username', 'reviewer__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ['review_request', 'reviewer', 'code_quality_score', 'reviewed_at']
    list_filter = ['reviewed_at', 'code_quality_score']
    search_fields = ['reviewer__username', 'review_request__title']
    readonly_fields = ['reviewed_at']


@admin.register(CodeReviewComment)
class CodeReviewCommentAdmin(admin.ModelAdmin):
    list_display = ['review', 'line_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__reviewer__username', 'comment']


@admin.register(ReviewerRating)
class ReviewerRatingAdmin(admin.ModelAdmin):
    list_display = ['review', 'rated_by', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['review__reviewer__username', 'rated_by__username']


@admin.register(ReviewerStats)
class ReviewerStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_reviews', 'average_rating', 'is_mentor', 'mentor_level', 'total_coins_earned']
    list_filter = ['is_mentor', 'mentor_level']
    search_fields = ['user__username']
