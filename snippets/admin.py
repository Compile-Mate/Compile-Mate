from django.contrib import admin
from .models import SnippetCategory, Snippet, SnippetTag, SnippetComment, SnippetCollection


@admin.register(SnippetCategory)
class SnippetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'display_order']
    list_editable = ['display_order']


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'language', 'visibility', 'stars_count', 'views', 'created_at']
    list_filter = ['language', 'visibility', 'created_at']
    search_fields = ['title', 'author__username', 'description']
    readonly_fields = ['views', 'stars_count', 'forks_count', 'created_at']
    filter_horizontal = ['tags', 'stars']


@admin.register(SnippetTag)
class SnippetTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']


@admin.register(SnippetComment)
class SnippetCommentAdmin(admin.ModelAdmin):
    list_display = ['snippet', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['snippet__title', 'author__username']


@admin.register(SnippetCollection)
class SnippetCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'owner__username']
    filter_horizontal = ['snippets']
