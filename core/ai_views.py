"""
AI-Powered Feature Views
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from problems.models import Problem, Submission
from .ai_tutor import ai_tutor, ai_problem_generator


@login_required
@require_http_methods(["POST"])
def ai_get_hint(request):
    """Get an AI-generated hint for a problem."""
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        user_code = data.get('code', '')
        hint_level = int(data.get('hint_level', 1))
        
        problem = get_object_or_404(Problem, id=problem_id)
        
        # Check if user has enough coins (cost: 10 coins per hint)
        hint_cost = 10
        if request.user.coins < hint_cost:
            return JsonResponse({
                'success': False,
                'error': 'Insufficient coins. Need 10 coins for a hint.'
            }, status=400)
        
        # Get hint from AI
        result = ai_tutor.get_hint(
            problem_description=problem.description,
            user_code=user_code,
            hint_level=hint_level
        )
        
        if result['success']:
            # Deduct coins
            request.user.coins -= hint_cost
            request.user.save()
            
            result['coins_deducted'] = hint_cost
            result['remaining_coins'] = request.user.coins
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_explain_error(request):
    """Get AI explanation for an error."""
    try:
        data = json.loads(request.body)
        error_message = data.get('error_message', '')
        user_code = data.get('code', '')
        language = data.get('language', 'python')
        
        # Free feature - no coin cost
        result = ai_tutor.explain_error(
            error_message=error_message,
            user_code=user_code,
            language=language
        )
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_review_code(request):
    """Get AI code review for a submission."""
    try:
        data = json.loads(request.body)
        submission_id = data.get('submission_id')
        
        submission = get_object_or_404(Submission, id=submission_id, user=request.user)
        problem = submission.problem
        
        # Check if user has enough coins (cost: 50 coins for code review)
        review_cost = 50
        if request.user.coins < review_cost:
            return JsonResponse({
                'success': False,
                'error': 'Insufficient coins. Need 50 coins for code review.'
            }, status=400)
        
        # Get review from AI
        result = ai_tutor.review_code(
            code=submission.code,
            language=submission.language,
            problem_description=problem.description
        )
        
        if result['success']:
            # Deduct coins
            request.user.coins -= review_cost
            request.user.save()
            
            result['coins_deducted'] = review_cost
            result['remaining_coins'] = request.user.coins
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_suggest_test_cases(request):
    """Get AI-suggested test cases for a problem."""
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        
        problem = get_object_or_404(Problem, id=problem_id)
        
        # Free feature for problem creators
        if problem.created_by != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Only problem creators can generate test cases.'
            }, status=403)
        
        # Get test case suggestions
        result = ai_tutor.suggest_test_cases(
            problem_description=problem.description,
            constraints=problem.constraints or ""
        )
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def ai_tutor_dashboard(request):
    """AI Tutor dashboard page."""
    # Get user's AI usage stats (you can track this in a separate model)
    context = {
        'user_coins': request.user.coins,
        'hint_cost': 10,
        'review_cost': 50,
    }
    return render(request, 'core/ai_tutor_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def ai_generate_problem(request):
    """Generate a new problem using AI (admin only)."""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Only staff can generate problems.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        difficulty = data.get('difficulty', 'medium')
        topics = data.get('topics', [])
        style = data.get('style', 'competitive')
        
        if not topics:
            return JsonResponse({
                'success': False,
                'error': 'At least one topic is required.'
            }, status=400)
        
        # Generate problem
        result = ai_problem_generator.generate_problem(
            difficulty=difficulty,
            topics=topics,
            style=style
        )
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def ai_problem_generator_page(request):
    """AI Problem Generator page (admin only)."""
    if not request.user.is_staff:
        return render(request, 'core/403.html', status=403)
    
    # Available topics
    topics = [
        'arrays', 'strings', 'linked-lists', 'trees', 'graphs',
        'dynamic-programming', 'greedy', 'backtracking', 'sorting',
        'searching', 'hashing', 'stacks', 'queues', 'heaps',
        'bit-manipulation', 'math', 'recursion', 'two-pointers',
        'sliding-window', 'binary-search'
    ]
    
    context = {
        'topics': topics,
        'difficulties': ['easy', 'medium', 'hard'],
        'styles': ['competitive', 'interview', 'educational'],
    }
    return render(request, 'core/ai_problem_generator.html', context)

