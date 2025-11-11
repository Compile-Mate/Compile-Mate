from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CodeReview, CodeReviewRequest, CodeReviewComment
from problems.models import Problem, Submission


@login_required
def review_list(request):
    """List all code review requests."""
    # Reviews I'm giving
    my_reviews = CodeReview.objects.filter(reviewer=request.user).select_related('review_request').order_by('-reviewed_at')
    
    # Reviews I've requested
    my_requests = CodeReviewRequest.objects.filter(requester=request.user).order_by('-created_at')
    
    # Open review requests (available for me to pick up)
    open_requests = CodeReviewRequest.objects.filter(status='open').exclude(requester=request.user).order_by('-created_at')[:10]
    
    context = {
        'my_reviews': my_reviews,
        'my_requests': my_requests,
        'open_requests': open_requests,
    }
    return render(request, 'code_reviews/review_list.html', context)


@login_required
def request_review(request):
    """Request a code review for a submission."""
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        submission = get_object_or_404(Submission, id=submission_id, user=request.user)
        
        # Check if review already requested
        if CodeReviewRequest.objects.filter(submission=submission, status__in=['open', 'in_review']).exists():
            messages.warning(request, 'Review already requested for this submission.')
            return redirect('code_reviews:list')
        
        CodeReviewRequest.objects.create(
            requester=request.user,
            submission=submission,
            title=title,
            description=description,
            status='open'
        )
        
        messages.success(request, 'Code review requested successfully!')
        return redirect('code_reviews:list')
    
    # Get user's accepted submissions
    submissions = Submission.objects.filter(
        user=request.user,
        status='accepted'
    ).select_related('problem').order_by('-submitted_at')[:20]
    
    context = {'submissions': submissions}
    return render(request, 'code_reviews/request_review.html', context)


@login_required
def review_detail(request, review_id):
    """View review request details."""
    review_request = get_object_or_404(
        CodeReviewRequest.objects.select_related('requester', 'submission', 'submission__problem', 'reviewer'),
        id=review_id
    )
    
    # Check permissions
    is_owner = request.user == review_request.requester
    is_reviewer = request.user == review_request.reviewer
    
    if not (is_owner or is_reviewer):
        # Allow others to view open requests
        if review_request.status != 'open':
            messages.error(request, 'You do not have permission to view this review.')
            return redirect('code_reviews:list')
    
    # Get the actual review if completed
    try:
        review = review_request.review
        comments = review.comments.all().order_by('line_number')
    except CodeReview.DoesNotExist:
        review = None
        comments = []
    
    context = {
        'review_request': review_request,
        'review': review,
        'comments': comments,
        'is_owner': is_owner,
        'is_reviewer': is_reviewer,
    }
    return render(request, 'code_reviews/review_detail.html', context)
