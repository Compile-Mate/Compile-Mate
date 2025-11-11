"""
CompileMate Judge Views
======================
Views for code submission and execution using our custom Docker-based execution engine.
"""

import json
import re
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from problems.models import Problem, TestCase, Submission
from users.models import User
from django.utils import timezone

# Import our custom executor and tasks
from .executor import execute_code, execute_test_cases
from .tasks import execute_submission_task, execute_custom_test_task

# Language mapping for consistent naming
LANGUAGE_MAP = {
    'python': 'python',
    'cpp': 'cpp',
    'java': 'java',
    'javascript': 'javascript',
}


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SubmitCodeView(View):
    """
    Handle code submission for both 'Run Code' and 'Submit Solution'.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Process code submission.
        
        Parameters:
            - code: Source code
            - language: Programming language
            - problem_id: Problem ID
            - run_mode: 'run' (test with samples) or 'submit' (full submission)
            - input: Custom input (for custom test mode)
        """
        code = request.POST.get('code', '')
        language = request.POST.get('language', '').lower()
        problem_id = request.POST.get('problem_id')
        run_mode = request.POST.get('run_mode', 'submit')  # 'run' or 'submit'
        custom_input = request.POST.get('input', '')  # For custom testing
        
        user = request.user
        
        # Validation
        if not code or not language:
            return JsonResponse({'error': 'Missing code or language'}, status=400)
        
        if language not in LANGUAGE_MAP:
            return JsonResponse({'error': f'Unsupported language: {language}'}, status=400)
        
        # Get problem
        if not problem_id:
            return JsonResponse({'error': 'Problem ID required'}, status=400)
        
        try:
            problem = Problem.objects.get(id=problem_id, status='published')
        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        
        # Handle different modes
        if run_mode == 'run':
            # Run Code Mode - Execute with sample test cases
            return self._run_code(request, problem, code, language)
        
        elif run_mode == 'custom':
            # Custom Test Mode - Execute with user-provided input
            return self._run_custom_test(request, problem, code, language, custom_input)
        
        else:
            # Submit Solution Mode - Full submission with all test cases
            return self._submit_solution(request, problem, code, language, user)
    
    def _run_code(self, request, problem, code, language):
        """
        Run code with sample (non-hidden) test cases.
        Returns results immediately (synchronous).
        """
        # Get sample test cases (non-hidden)
        sample_test_cases = TestCase.objects.filter(
            problem=problem,
            is_hidden=False
        ).order_by('order')[:3]  # Limit to first 3 samples
        
        if not sample_test_cases.exists():
            return JsonResponse({
                'error': 'No sample test cases available for this problem'
            }, status=404)
        
        # Prepare test data
        test_data = []
        for tc in sample_test_cases:
            test_data.append({
                'input': tc.input_data,
                'expected_output': tc.expected_output
            })
        
        # Execute test cases
        try:
            result = execute_test_cases(
                language=language,
                code=code,
                test_cases=test_data,
                timeout=5  # Default 5 seconds timeout
            )
            
            # Format response
            test_case_results = []
            all_passed = True
            for tc_result in result['results']:
                test_passed = tc_result['passed']
                if not test_passed:
                    all_passed = False
                    
                test_case_results.append({
                    'test_case': tc_result['test_case'],
                    'status': 'passed' if test_passed else 'failed',
                    'input': tc_result['input'],
                    'expected': tc_result['expected_output'],
                    'output': tc_result['actual_output'],
                    'error_message': tc_result['stderr'] if tc_result['stderr'] else '',
                    'execution_time': tc_result['execution_time'],
                    'memory_used': tc_result['memory_used']
                })
            
            return JsonResponse({
                'status': 'Accepted' if all_passed else 'Wrong Answer',
                'test_cases': test_case_results,
                'total_tests': result['total_tests'],
                'passed': result['passed'],
                'failed': result['failed'],
                'execution_time': f"{result['total_time']:.3f}",
                'memory_used': max([tc['memory_used'] for tc in test_case_results]) if test_case_results else 0,
                'message': f"Executed {result['passed']}/{result['total_tests']} sample test cases"
            })
        
        except Exception as e:
            import traceback
            print(f"Error in _run_code: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'Runtime Error',
                'error': f'Execution error: {str(e)}',
                'error_message': str(e),
                'test_cases': []
            })
    
    def _run_custom_test(self, request, problem, code, language, custom_input):
        """
        Run code with custom user-provided input.
        Returns output immediately (synchronous).
        """
        try:
            result = execute_code(
                language=language,
                code=code,
                stdin=custom_input,
                timeout=10  # Default 10 seconds timeout
            )
            
            return JsonResponse({
                'status': result['status'],
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'execution_time': result['execution_time'],
                'memory_used': result['memory_used'],
                'compile_output': result.get('compile_output', '')
            })
        
        except Exception as e:
            return JsonResponse({
                'error': f'Execution error: {str(e)}'
            }, status=500)
    
    def _submit_solution(self, request, problem, code, language, user):
        """
        Submit solution for full auto-grading against all test cases.
        Executes synchronously and returns immediate results.
        """
        # Get all test cases
        test_cases = TestCase.objects.filter(problem=problem).order_by('order')
        
        if not test_cases.exists():
            return JsonResponse({
                'error': 'No test cases available for this problem'
            }, status=404)
        
        # Prepare test data
        test_data = []
        for tc in test_cases:
            test_data.append({
                'input': tc.input_data,
                'expected_output': tc.expected_output
            })
        
        # Execute test cases
        try:
            result = execute_test_cases(
                language=language,
                code=code,
                test_cases=test_data,
                timeout=5  # Default 5 seconds timeout
            )
            
            # Determine overall status
            all_passed = result['passed'] == result['total_tests']
            status = 'Accepted' if all_passed else 'Wrong Answer'
            
            # Create submission record
            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=code,
                language=language,
                status='accepted' if all_passed else 'wrong_answer',
                execution_time=result['total_time'],
                memory_used=0,
                score=100 if all_passed else int((result['passed'] / result['total_tests']) * 100)
            )
            
            # Update problem stats
            problem.total_submissions += 1
            if all_passed:
                problem.successful_submissions += 1
            problem.save()
            
            # Update user stats if accepted
            if all_passed and problem not in user.solved_problems.all():
                user.solved_problems.add(problem)
                user.coins += problem.coin_reward
                user.xp += problem.xp_reward
                user.save()
            
            # Format test case results
            test_case_results = []
            for tc_result in result['results']:
                test_passed = tc_result['passed']
                test_case_results.append({
                    'test_case': tc_result['test_case'],
                    'status': 'passed' if test_passed else 'failed',
                    'input': tc_result['input'],
                    'expected': tc_result['expected_output'],
                    'output': tc_result['actual_output'],
                    'error_message': tc_result['stderr'] if tc_result['stderr'] else '',
                    'execution_time': tc_result['execution_time'],
                    'memory_used': tc_result['memory_used']
                })
            
            return JsonResponse({
                'status': status,
                'test_cases': test_case_results,
                'total_tests': result['total_tests'],
                'passed': result['passed'],
                'failed': result['failed'],
                'execution_time': f"{result['total_time']:.3f}",
                'memory_used': max([tc['memory_used'] for tc in test_case_results]) if test_case_results else 0,
                'submission_id': submission.id,
                'message': f"Passed {result['passed']}/{result['total_tests']} test cases"
            })
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return JsonResponse({
                'status': 'Runtime Error',
                'error': f'Execution error: {str(e)}',
                'error_message': str(e),
                'test_cases': []
            }, status=500)


@csrf_exempt
@login_required
def get_submission_status(request, submission_id):
    """
    Poll endpoint to check submission status.
    Used by frontend to get real-time updates on submission evaluation.
    """
    try:
        submission = Submission.objects.get(id=submission_id, user=request.user)
        
        response_data = {
            'submission_id': submission.id,
            'status': submission.status,
            'execution_time': submission.execution_time,
            'memory_used': submission.memory_used,
            'score': submission.score or 0,
        }
        
        # Add detailed results if available
        if submission.status in ['accepted', 'wrong_answer', 'runtime_error']:
            response_data['test_results'] = submission.test_results or []
            response_data['error_message'] = submission.error_message or ''
            response_data['test_cases_passed'] = sum(
                1 for r in submission.test_results if r.get('passed', False)
            ) if submission.test_results else 0
            response_data['total_test_cases'] = len(submission.test_results) if submission.test_results else 0
        
        return JsonResponse(response_data)
    
    except Submission.DoesNotExist:
        return JsonResponse({'error': 'Submission not found'}, status=404)


@csrf_exempt
@login_required
def quick_test(request):
    """
    Quick test endpoint for immediate code execution without creating a submission.
    Useful for debugging and testing.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    code = request.POST.get('code', '')
    language = request.POST.get('language', '').lower()
    stdin = request.POST.get('input', '')
    
    if not code or not language:
        return JsonResponse({'error': 'Missing code or language'}, status=400)
    
    if language not in LANGUAGE_MAP:
        return JsonResponse({'error': f'Unsupported language: {language}'}, status=400)
    
    try:
        result = execute_code(
            language=language,
            code=code,
            stdin=stdin,
            timeout=10
        )
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Execution error: {str(e)}'
        }, status=500)


@login_required
def supported_languages(request):
    """
    Return list of supported programming languages.
    """
    languages = [
        {
            'id': 'python',
            'name': 'Python 3',
            'version': '3.11',
            'extensions': ['.py']
        },
        {
            'id': 'cpp',
            'name': 'C++',
            'version': 'GCC 14',
            'extensions': ['.cpp', '.cc']
        },
        {
            'id': 'java',
            'name': 'Java',
            'version': '17',
            'extensions': ['.java']
        },
        {
            'id': 'javascript',
            'name': 'JavaScript',
            'version': 'Node.js 18',
            'extensions': ['.js']
        },
    ]
    
    return JsonResponse({'languages': languages})
