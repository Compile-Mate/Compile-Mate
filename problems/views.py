from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Problem, Submission, Tag, ProblemDiscussion
from .forms import SubmissionForm


def problem_list(request):
    """Display list of all problems."""
    problems = Problem.objects.filter(status='published').order_by('-created_at')
    
    # Filtering
    difficulty = request.GET.get('difficulty')
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    tag = request.GET.get('tag')
    if tag:
        problems = problems.filter(tags__name=tag)
    
    # Search
    search = request.GET.get('search')
    if search:
        problems = problems.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    # Pagination
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all tags for filter
    tags = Tag.objects.all()
    
    context = {
        'page_obj': page_obj,
        'tags': tags,
        'difficulty_filter': difficulty,
        'tag_filter': tag,
        'search_query': search,
    }
    return render(request, 'problems/problem_list.html', context)


def api_problem_list(request):
    """API endpoint to list all problems for AI Tutor."""
    problems = Problem.objects.filter(status='published').order_by('-created_at')
    
    problems_data = [{
        'id': p.id,
        'title': p.title,
        'difficulty': p.difficulty,
        'total_submissions': p.total_submissions,
    } for p in problems]
    
    return JsonResponse({'problems': problems_data})


def problem_detail(request, slug):
    """Display problem details."""
    problem = get_object_or_404(Problem, slug=slug, status='published')
    
    # Get user's submissions for this problem
    user_submissions = []
    if request.user.is_authenticated:
        user_submissions = Submission.objects.filter(
            user=request.user, 
            problem=problem
        ).order_by('-submitted_at')[:5]
    
    # Get discussions
    discussions = ProblemDiscussion.objects.filter(
        problem=problem, 
        parent=None
    ).order_by('-created_at')[:10]
    
    context = {
        'problem': problem,
        'user_submissions': user_submissions,
        'discussions': discussions,
    }
    return render(request, 'problems/problem_detail.html', context)


@login_required
def problem_solve(request, slug):
    """Problem solving page with code editor."""
    problem = get_object_or_404(Problem, slug=slug, status='published')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.problem = problem
            submission.save()
            
            # TODO: Send to judge for evaluation
            messages.success(request, 'Code submitted successfully!')
            return redirect('problems:submission_detail', submission_id=submission.id)
    else:
        form = SubmissionForm()
    
    context = {
        'problem': problem,
        'form': form,
    }
    return render(request, 'problems/problem_solve.html', context)


@login_required
def submission_detail(request, submission_id):
    """Display submission details and results."""
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    
    context = {
        'submission': submission,
    }
    return render(request, 'problems/submission_detail.html', context)


@login_required
def user_submissions(request):
    """Display user's submission history."""
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
    
    # Filtering
    status = request.GET.get('status')
    if status:
        submissions = submissions.filter(status=status)
    
    problem = request.GET.get('problem')
    if problem:
        submissions = submissions.filter(problem__title__icontains=problem)
    
    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'problem_filter': problem,
    }
    return render(request, 'problems/user_submissions.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_code(request, slug):
    return HttpResponse("Code submission endpoint (to be implemented)")


def leaderboard(request):
    """Display problem solving leaderboard."""
    # Get users with most problems solved
    from django.db.models import Count
    from users.models import User
    
    top_solvers = User.objects.annotate(
        solved_count=Count('submissions', filter=Q(submissions__status='accepted'))
    ).filter(solved_count__gt=0).order_by('-solved_count', '-xp')[:50]
    
    context = {
        'top_solvers': top_solvers,
    }
    return render(request, 'problems/leaderboard.html', context) 