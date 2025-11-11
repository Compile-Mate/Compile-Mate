from django.contrib import admin
from .models import LearningPath, Topic, PathModule, ModuleProblem, PathEnrollment, PathRating, Editorial


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'enrolled_count', 'completed_count', 'completion_rate', 'is_published', 'is_featured']
    list_filter = ['difficulty', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['topics']
    
    def completion_rate(self, obj):
        return f"{obj.completion_rate:.1f}%"
    completion_rate.short_description = 'Completion Rate'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'display_order']
    list_editable = ['display_order']


@admin.register(PathModule)
class PathModuleAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'title', 'order', 'is_locked']
    list_filter = ['learning_path', 'is_locked']
    search_fields = ['title']
    filter_horizontal = ['problems']


@admin.register(ModuleProblem)
class ModuleProblemAdmin(admin.ModelAdmin):
    list_display = ['module', 'problem', 'order', 'is_optional']
    list_filter = ['is_optional']


@admin.register(PathEnrollment)
class PathEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_path', 'status', 'progress_percentage', 'enrolled_at', 'completed_at']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['user__username', 'learning_path__title']
    filter_horizontal = ['completed_modules']


@admin.register(PathRating)
class PathRatingAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'learning_path__title']


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ['problem', 'author', 'views', 'likes_count', 'is_official', 'is_published', 'created_at']
    list_filter = ['is_official', 'is_published', 'created_at']
    search_fields = ['problem__title', 'author__username', 'title']
    readonly_fields = ['views', 'likes_count']
