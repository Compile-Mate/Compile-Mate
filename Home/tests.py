from django.test import TestCase
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
from .runcode import CodeExecutor, ExecutionStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"

@dataclass
class TestCase:
    input_data: str
    expected_output: str
    description: Optional[str] = None
    timeout: float = 2.0
    points: float = 1.0
    hidden: bool = False

@dataclass
class TestResult:
    status: TestStatus
    actual_output: str = ""
    error_message: str = ""
    runtime_ms: float = 0
    memory_mb: float = 0
    points_earned: float = 0
    hidden: bool = False

class TestSuite:
    def __init__(self, name: str, language: str):
        self.name = name
        self.language = language
        self.test_cases: List[TestCase] = []
        self.setup_code: str = ""
        self.teardown_code: str = ""
        self.total_points: float = 0

    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(test_case)
        self.total_points += test_case.points

    def add_test_cases(self, test_cases: List[TestCase]):
        for test_case in test_cases:
            self.add_test_case(test_case)

class TestRunner:
    def __init__(self, max_workers: int = 4, timeout: float = 10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run_suite(self, suite: TestSuite, code: str) -> Dict[str, Any]:
        """Run all test cases in the suite"""
        start_time = time.time()
        results = []
        total_points = 0
        passed_count = 0

        # Run setup code if any
        if suite.setup_code:
            setup_result = self._run_setup(suite)
            if not setup_result['success']:
                return {
                    'status': 'setup_failed',
                    'error': setup_result['error'],
                    'results': [],
                    'points': 0,
                    'max_points': suite.total_points,
                    'runtime_ms': 0
                }

        # Run test cases in parallel
        futures = []
        for test_case in suite.test_cases:
            future = self.executor.submit(
                self._run_test_case,
                code,
                test_case,
                suite.language
            )
            futures.append((test_case, future))

        # Collect results
        for test_case, future in futures:
            try:
                result = future.result(timeout=self.timeout)
                if result.status == TestStatus.PASSED:
                    passed_count += 1
                    total_points += test_case.points
                results.append(result)
            except Exception as e:
                logger.error(f"Error running test case: {str(e)}")
                results.append(TestResult(
                    status=TestStatus.ERROR,
                    error_message=str(e)
                ))

        # Run teardown code if any
        if suite.teardown_code:
            teardown_result = self._run_teardown(suite)
            if not teardown_result['success']:
                logger.warning(f"Teardown failed: {teardown_result['error']}")

        end_time = time.time()
        runtime_ms = (end_time - start_time) * 1000

        return {
            'status': 'completed',
            'results': [self._format_result(r) for r in results],
            'summary': {
                'total_tests': len(suite.test_cases),
                'passed': passed_count,
                'failed': len(suite.test_cases) - passed_count,
                'points': total_points,
                'max_points': suite.total_points,
                'runtime_ms': runtime_ms
            }
        }

    def _run_test_case(self, code: str, test_case: TestCase, language: str) -> TestResult:
        """Run a single test case"""
        try:
            with CodeExecutor(language) as executor:
                result = executor.run_code(code, test_case.input_data)

                if result.status != ExecutionStatus.SUCCESS:
                    return TestResult(
                        status=TestStatus.ERROR,
                        error_message=result.error_message,
                        runtime_ms=result.runtime_ms,
                        memory_mb=result.memory_mb,
                        points_earned=0,
                        hidden=test_case.hidden
                    )

                # Compare output
                expected = test_case.expected_output.strip()
                actual = result.stdout.strip()
                status = TestStatus.PASSED if expected == actual else TestStatus.FAILED
                points = test_case.points if status == TestStatus.PASSED else 0

                return TestResult(
                    status=status,
                    actual_output=actual,
                    runtime_ms=result.runtime_ms,
                    memory_mb=result.memory_mb,
                    points_earned=points,
                    hidden=test_case.hidden
                )

        except Exception as e:
            logger.error(f"Error in test case execution: {str(e)}")
            return TestResult(
                status=TestStatus.ERROR,
                error_message=str(e),
                points_earned=0,
                hidden=test_case.hidden
            )

    def _run_setup(self, suite: TestSuite) -> Dict[str, Any]:
        """Run suite setup code"""
        try:
            with CodeExecutor(suite.language) as executor:
                result = executor.run_code(suite.setup_code)
                return {
                    'success': result.status == ExecutionStatus.SUCCESS,
                    'error': result.error_message if result.status != ExecutionStatus.SUCCESS else None
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _run_teardown(self, suite: TestSuite) -> Dict[str, Any]:
        """Run suite teardown code"""
        try:
            with CodeExecutor(suite.language) as executor:
                result = executor.run_code(suite.teardown_code)
                return {
                    'success': result.status == ExecutionStatus.SUCCESS,
                    'error': result.error_message if result.status != ExecutionStatus.SUCCESS else None
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _format_result(self, result: TestResult) -> Dict[str, Any]:
        """Format test result for output"""
        formatted = {
            'status': result.status.value,
            'runtime_ms': result.runtime_ms,
            'memory_mb': result.memory_mb,
            'points_earned': result.points_earned
        }

        if not result.hidden:
            formatted.update({
                'actual_output': result.actual_output,
                'error_message': result.error_message
            })

        return formatted

class TestCaseGenerator:
    """Generate test cases for different problem types"""

    @staticmethod
    def generate_array_test_cases(
        min_size: int = 1,
        max_size: int = 100,
        min_value: int = -1000,
        max_value: int = 1000,
        num_cases: int = 10
    ) -> List[TestCase]:
        """Generate test cases for array-based problems"""
        import random
        test_cases = []

        for i in range(num_cases):
            size = random.randint(min_size, max_size)
            arr = [random.randint(min_value, max_value) for _ in range(size)]
            
            test_cases.append(TestCase(
                input_data=json.dumps(arr),
                expected_output="",  # To be filled by problem-specific logic
                description=f"Random array test case {i+1}",
                hidden=i >= 2  # First two test cases visible to users
            ))

        return test_cases

    @staticmethod
    def generate_string_test_cases(
        min_length: int = 1,
        max_length: int = 100,
        char_set: str = "abcdefghijklmnopqrstuvwxyz",
        num_cases: int = 10
    ) -> List[TestCase]:
        """Generate test cases for string-based problems"""
        import random
        test_cases = []

        for i in range(num_cases):
            length = random.randint(min_length, max_length)
            s = ''.join(random.choice(char_set) for _ in range(length))
            
            test_cases.append(TestCase(
                input_data=s,
                expected_output="",  # To be filled by problem-specific logic
                description=f"Random string test case {i+1}",
                hidden=i >= 2
            ))

        return test_cases

class TestReport:
    """Generate detailed test reports"""

    @staticmethod
    def generate_html_report(results: Dict[str, Any]) -> str:
        """Generate an HTML report from test results"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { margin-bottom: 20px; }
                .test-case { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; }
                .passed { background-color: #dff0d8; }
                .failed { background-color: #f2dede; }
                .error { background-color: #fcf8e3; }
                .metrics { color: #666; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>Test Results</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: {passed}</p>
                <p>Failed: {failed}</p>
                <p>Points: {points}/{max_points}</p>
                <p>Total Runtime: {runtime_ms:.2f}ms</p>
            </div>
            <div class="test-cases">
                <h2>Test Cases</h2>
                {test_cases}
            </div>
        </body>
        </html>
        """

        test_case_template = """
        <div class="test-case {status}">
            <h3>Test Case {index}</h3>
            <p>Status: {status}</p>
            <div class="metrics">
                <p>Runtime: {runtime_ms:.2f}ms</p>
                <p>Memory: {memory_mb:.2f}MB</p>
                <p>Points: {points_earned}</p>
            </div>
            {details}
        </div>
        """

        # Format test cases
        test_cases_html = []
        for i, result in enumerate(results['results'], 1):
            details = ""
            if not result.get('hidden', False):
                if result['status'] != 'passed':
                    details = f"<p>Error: {result.get('error_message', '')}</p>"
                    if 'actual_output' in result:
                        details += f"<p>Actual Output: {result['actual_output']}</p>"

            test_cases_html.append(test_case_template.format(
                index=i,
                status=result['status'],
                runtime_ms=result['runtime_ms'],
                memory_mb=result['memory_mb'],
                points_earned=result['points_earned'],
                details=details
            ))

        # Format summary
        summary = results['summary']
        return template.format(
            total_tests=summary['total_tests'],
            passed=summary['passed'],
            failed=summary['failed'],
            points=summary['points'],
            max_points=summary['max_points'],
            runtime_ms=summary['runtime_ms'],
            test_cases='\n'.join(test_cases_html)
        )
