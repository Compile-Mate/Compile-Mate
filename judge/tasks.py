"""
Celery Tasks for Code Execution
================================
Background tasks for running code submissions asynchronously.
"""

from celery import shared_task
from django.utils import timezone
from .models import JudgeSubmission, TestCaseResult
from .executor import execute_test_cases
from problems.models import Submission, Problem, TestCase
from users.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def execute_submission_task(self, submission_id: int):
    """
    Execute a code submission against all test cases.
    
    Args:
        submission_id: ID of the Submission to execute
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        problem = submission.problem
        
        # Update status to running
        submission.status = 'running'
        submission.save()
        
        # Get all test cases for the problem
        test_cases = TestCase.objects.filter(problem=problem).order_by('id')
        
        if not test_cases.exists():
            submission.status = 'error'
            submission.error_message = 'No test cases found for this problem'
            submission.save()
            return
        
        # Prepare test cases in the format expected by executor
        test_data = []
        for tc in test_cases:
            test_data.append({
                'input': tc.input_data,
                'expected_output': tc.expected_output
            })
        
        # Execute against all test cases
        logger.info(f"Executing submission {submission_id} for problem {problem.slug}")
        
        result = execute_test_cases(
            language=submission.language,
            code=submission.code,
            test_cases=test_data,
            timeout=problem.time_limit or 5
        )
        
        # Update submission with results
        submission.status = result['overall_status'].lower()
        submission.execution_time = result['total_time']
        submission.memory_used = max(
            [r['memory_used'] for r in result['results']], default=0
        )
        
        # Calculate score
        if result['passed'] > 0:
            submission.score = (result['passed'] / result['total_tests']) * 100
        else:
            submission.score = 0
        
        # Store individual test case results
        submission.test_results = result['results']
        
        # Check if all tests passed
        if result['failed'] == 0:
            submission.status = 'accepted'
            
            # Award coins and XP to user
            award_submission_rewards.delay(submission_id)
        else:
            submission.status = 'wrong_answer'
        
        submission.save()
        
        logger.info(
            f"Submission {submission_id} completed: "
            f"{result['passed']}/{result['total_tests']} passed"
        )
        
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
    except Exception as e:
        logger.error(f"Error executing submission {submission_id}: {str(e)}")
        
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.status = 'error'
            submission.error_message = str(e)
            submission.save()
        except Exception:
            pass
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@shared_task
def award_submission_rewards(submission_id: int):
    """
    Award MateCoins and XP for successful submission.
    
    Args:
        submission_id: ID of the accepted submission
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        user = submission.user
        problem = submission.problem
        
        # Check if this is the first accepted submission for this problem
        previous_accepted = Submission.objects.filter(
            user=user,
            problem=problem,
            status='accepted',
            created_at__lt=submission.created_at
        ).exists()
        
        if not previous_accepted:
            # Award coins and XP
            coins = problem.coin_reward or 10
            xp = problem.xp_reward or 20
            
            user.coins += coins
            user.xp += xp
            
            # Level up logic
            required_xp = user.level * 100
            if user.xp >= required_xp:
                user.level += 1
                user.xp = 0  # Reset XP for next level
            
            user.save()
            
            # Create coin transaction
            from users.models import CoinTransaction
            CoinTransaction.objects.create(
                user=user,
                amount=coins,
                transaction_type='problem_solved',
                description=f'Solved: {problem.title}'
            )
            
            logger.info(
                f"Awarded {coins} coins and {xp} XP to user {user.username} "
                f"for solving {problem.title}"
            )
    
    except Exception as e:
        logger.error(f"Error awarding rewards for submission {submission_id}: {str(e)}")


@shared_task
def execute_custom_test_task(submission_id: int, test_input: str):
    """
    Execute code with custom input (for testing/debugging).
    
    Args:
        submission_id: ID of the submission
        test_input: Custom input to test with
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        from .executor import execute_code
        
        result = execute_code(
            language=submission.language,
            code=submission.code,
            stdin=test_input,
            timeout=10
        )
        
        # Store result in cache or database
        from django.core.cache import cache
        cache_key = f'custom_test_{submission_id}'
        cache.set(cache_key, result, timeout=300)  # 5 minutes
        
        logger.info(f"Custom test executed for submission {submission_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error executing custom test: {str(e)}")
        return {
            'success': False,
            'status': 'Error',
            'stdout': '',
            'stderr': str(e)
        }


@shared_task
def cleanup_old_submissions():
    """
    Periodic task to cleanup old submission data.
    Run this daily to keep database size manageable.
    """
    from datetime import timedelta
    
    try:
        # Delete submissions older than 90 days with status 'error' or 'wrong_answer'
        cutoff_date = timezone.now() - timedelta(days=90)
        
        deleted_count = Submission.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['error', 'wrong_answer']
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old submissions")
        
    except Exception as e:
        logger.error(f"Error cleaning up submissions: {str(e)}")

