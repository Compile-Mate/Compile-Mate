from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from problems.models import Submission


class CodeReviewRequest(models.Model):
    """Model for code review requests."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_requests_made')
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='review_requests')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="What specific feedback are you looking for?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Reviewer assignment
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_assignments')
    
    # Rewards
    coin_offer = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review Request: {self.title} by {self.requester.username}"


class CodeReview(models.Model):
    """Model for code reviews."""
    
    review_request = models.OneToOneField(CodeReviewRequest, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    
    # Review content
    overall_feedback = models.TextField()
    strengths = models.TextField(help_text="What was done well")
    improvements = models.TextField(help_text="What could be improved")
    code_quality_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    time_complexity_feedback = models.TextField(blank=True)
    space_complexity_feedback = models.TextField(blank=True)
    
    # Recommendations
    alternative_approach = models.TextField(blank=True)
    resources = models.TextField(blank=True, help_text="Learning resources")
    
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reviewed_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.review_request.requester.username}"


class CodeReviewComment(models.Model):
    """Model for line-by-line comments on code."""
    
    review = models.ForeignKey(CodeReview, on_delete=models.CASCADE, related_name='comments')
    line_number = models.IntegerField()
    comment = models.TextField()
    suggestion = models.TextField(blank=True, help_text="Suggested improvement")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['line_number', 'created_at']
    
    def __str__(self):
        return f"Comment on line {self.line_number}"


class ReviewerRating(models.Model):
    """Model for rating reviewers."""
    
    review = models.OneToOneField(CodeReview, on_delete=models.CASCADE, related_name='rating')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rating}⭐ for {self.review.reviewer.username}"


class ReviewerStats(models.Model):
    """Model for reviewer statistics."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reviewer_stats')
    total_reviews = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    total_coins_earned = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0, help_text="Number of 'helpful' votes")
    is_mentor = models.BooleanField(default=False)
    mentor_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    class Meta:
        verbose_name_plural = 'Reviewer stats'
    
    def __str__(self):
        return f"{self.user.username} - {self.total_reviews} reviews ({self.average_rating:.1f}⭐)"
    
    def update_stats(self, new_rating, coins_earned):
        """Update stats after a review."""
        self.total_reviews += 1
        self.total_coins_earned += coins_earned
        
        # Update average rating
        if self.average_rating == 0:
            self.average_rating = new_rating
        else:
            self.average_rating = (
                (self.average_rating * (self.total_reviews - 1) + new_rating) / self.total_reviews
            )
        
        # Level up mentor
        if self.total_reviews >= self.mentor_level * 10 and self.average_rating >= 4.0:
            self.mentor_level = min(self.mentor_level + 1, 10)
        
        self.save()
