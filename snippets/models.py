from django.db import models
from users.models import User


class SnippetCategory(models.Model):
    """Model for snippet categories."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="📝")
    display_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Snippet categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Snippet(models.Model):
    """Model for code snippets."""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('other', 'Other'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('unlisted', 'Unlisted'),
        ('public', 'Public'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippets')
    
    # Code
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    
    # Organization
    category = models.ForeignKey(SnippetCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='snippets')
    tags = models.ManyToManyField('SnippetTag', related_name='snippets', blank=True)
    
    # Visibility
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Engagement
    views = models.IntegerField(default=0)
    stars = models.ManyToManyField(User, related_name='starred_snippets', blank=True)
    stars_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    
    # Forking
    forked_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forks')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['visibility', '-stars_count']),
            models.Index(fields=['language', '-stars_count']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def fork(self, user):
        """Create a fork of this snippet."""
        fork = Snippet.objects.create(
            title=f"{self.title} (Fork)",
            description=self.description,
            author=user,
            language=self.language,
            code=self.code,
            category=self.category,
            visibility='private',
            forked_from=self
        )
        fork.tags.set(self.tags.all())
        self.forks_count += 1
        self.save()
        return fork


class SnippetTag(models.Model):
    """Model for snippet tags."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SnippetComment(models.Model):
    """Model for comments on snippets."""
    
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.snippet.title}"


class SnippetCollection(models.Model):
    """Model for organizing snippets into collections."""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_collections')
    snippets = models.ManyToManyField(Snippet, related_name='collections', blank=True)
    
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} by {self.owner.username}"
