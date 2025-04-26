import subprocess
import os
import signal
import threading
import tempfile
import json
import psutil
import platform
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import platform-specific modules
IS_WINDOWS = platform.system() == 'Windows'
if not IS_WINDOWS:
    import resource
else:
    import win32process
    import win32con
    import wmi

class ExecutionStatus(Enum):
    SUCCESS = "success"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    SECURITY_ERROR = "security_error"
    INTERNAL_ERROR = "internal_error"

@dataclass
class ExecutionResult:
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    runtime_ms: float = 0
    memory_mb: float = 0
    error_message: str = ""

class ResourceLimiter:
    @staticmethod
    def set_memory_limit(pid: int, max_memory_mb: int):
        """Set memory limit for a process in a platform-independent way"""
        try:
            if IS_WINDOWS:
                # On Windows, we can only monitor memory usage
                process = psutil.Process(pid)
                while process.is_running():
                    try:
                        memory_mb = process.memory_info().rss / (1024 * 1024)
                        if memory_mb > max_memory_mb:
                            process.kill()
                            break
                    except psutil.NoSuchProcess:
                        break
            else:
                # On Unix systems, we can use the resource module
                memory_bytes = max_memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except Exception as e:
            logger.error(f"Error setting memory limit: {str(e)}")

    @staticmethod
    def set_cpu_limit(pid: int, max_time_seconds: int):
        """Set CPU time limit for a process in a platform-independent way"""
        try:
            if IS_WINDOWS:
                # On Windows, we use a timer thread to kill the process
                def kill_on_timeout():
                    try:
                        process = psutil.Process(pid)
                        process.kill()
                    except psutil.NoSuchProcess:
                        pass

                timer = threading.Timer(max_time_seconds, kill_on_timeout)
                timer.start()
            else:
                # On Unix systems, we can use the resource module
                resource.setrlimit(resource.RLIMIT_CPU, (max_time_seconds, max_time_seconds))
        except Exception as e:
            logger.error(f"Error setting CPU limit: {str(e)}")

class LanguageConfig:
    CONFIGS = {
        'python': {
            'extension': '.py',
            'compile_cmd': None,
            'run_cmd': ['python3'] if not IS_WINDOWS else ['python'],
            'time_limit': 5,  # seconds
            'memory_limit': 512,  # MB
            'template': 'def solution(params):\n    # Write your code here\n    pass'
        },
        'cpp': {
            'extension': '.cpp',
            'compile_cmd': ['g++', '-std=c++17', '-O2', '-Wall', '-fsanitize=address'],
            'run_cmd': './a.out' if not IS_WINDOWS else 'a.exe',
            'time_limit': 2,
            'memory_limit': 512,
            'template': '''#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    // Write your function here
};'''
        },
        'java': {
            'extension': '.java',
            'compile_cmd': ['javac'],
            'run_cmd': ['java', '-Xmx512m'],
            'time_limit': 3,
            'memory_limit': 512,
            'template': '''public class Solution {
    // Write your function here
}'''
        }
    }

    @staticmethod
    def get_config(language: str) -> Dict[str, Any]:
        config = LanguageConfig.CONFIGS.get(language.lower())
        if not config:
            raise ValueError(f"Unsupported language: {language}")
        return config

class CodeExecutor:
    def __init__(self, language: str):
        self.language = language.lower()
        self.config = LanguageConfig.get_config(self.language)
        self.temp_dir = None
        self.process = None

    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            try:
                self.process.kill()
            except:
                pass
        if self.temp_dir:
            self.temp_dir.cleanup()

    def _get_memory_usage(self, pid: int) -> float:
        """Get memory usage of a process in MB"""
        try:
            process = psutil.Process(pid)
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0

    def compile_code(self, code: str) -> Tuple[bool, str]:
        """Compile the code if needed"""
        if not self.config['compile_cmd']:
            return True, ""

        file_path = os.path.join(self.temp_dir.name, f'solution{self.config["extension"]}')
        with open(file_path, 'w') as f:
            f.write(code)

        try:
            compile_process = subprocess.run(
                self.config['compile_cmd'] + [file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            return compile_process.returncode == 0, compile_process.stderr
        except subprocess.TimeoutExpired:
            return False, "Compilation timed out"
        except Exception as e:
            return False, str(e)

    def run_code(self, code: str, input_data: str = "") -> ExecutionResult:
        """Execute the code with the given input"""
        try:
            # Compile if needed
            if self.config['compile_cmd']:
                success, error = self.compile_code(code)
                if not success:
                    return ExecutionResult(
                        status=ExecutionStatus.COMPILATION_ERROR,
                        error_message=error
                    )

            # Prepare command
            if self.language == 'java':
                run_cmd = self.config['run_cmd'] + ['Solution']
            elif self.language == 'python':
                file_path = os.path.join(self.temp_dir.name, f'solution{self.config["extension"]}')
                with open(file_path, 'w') as f:
                    f.write(code)
                run_cmd = self.config['run_cmd'] + [file_path]
            else:
                run_cmd = [os.path.join(self.temp_dir.name, self.config['run_cmd'])]

            # Execute code with resource limits
            start_time = time.time()
            try:
                self.process = subprocess.Popen(
                    run_cmd,
                    stdin=subprocess.PIPE if input_data else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
                )

                # Set resource limits
                ResourceLimiter.set_memory_limit(self.process.pid, self.config['memory_limit'])
                ResourceLimiter.set_cpu_limit(self.process.pid, self.config['time_limit'])

                stdout, stderr = self.process.communicate(
                    input=input_data,
                    timeout=self.config['time_limit']
                )

                end_time = time.time()
                runtime_ms = (end_time - start_time) * 1000
                memory_mb = self._get_memory_usage(self.process.pid)

                if self.process.returncode != 0:
                    return ExecutionResult(
                        status=ExecutionStatus.RUNTIME_ERROR,
                        stderr=stderr,
                        runtime_ms=runtime_ms,
                        memory_mb=memory_mb,
                        error_message=stderr
                    )

                if memory_mb > self.config['memory_limit']:
                    return ExecutionResult(
                        status=ExecutionStatus.MEMORY_LIMIT_EXCEEDED,
                        runtime_ms=runtime_ms,
                        memory_mb=memory_mb,
                        error_message=f"Memory limit exceeded: {memory_mb:.2f}MB used"
                    )

                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    stdout=stdout,
                    runtime_ms=runtime_ms,
                    memory_mb=memory_mb
                )

            except subprocess.TimeoutExpired:
                if self.process:
                    self.process.kill()
                return ExecutionResult(
                    status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                    error_message=f"Time limit exceeded: >{self.config['time_limit']}s"
                )

        except Exception as e:
            logger.error(f"Internal error during code execution: {str(e)}")
            return ExecutionResult(
                status=ExecutionStatus.INTERNAL_ERROR,
                error_message=f"Internal error: {str(e)}"
            )

class TestRunner:
    def __init__(self, language: str):
        self.language = language
        self.executor = CodeExecutor(language)

    def run_test_cases(self, code: str, test_cases: list) -> Dict[str, Any]:
        """Run multiple test cases and return results"""
        results = []
        passed = 0
        total = len(test_cases)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for test_case in test_cases:
                future = executor.submit(self._run_single_test, code, test_case)
                futures.append(future)

            for future in futures:
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                    if result['passed']:
                        passed += 1
                except TimeoutError:
                    results.append({
                        'passed': False,
                        'status': 'Timeout',
                        'error': 'Test case execution timed out'
                    })

        return {
            'passed': passed,
            'total': total,
            'results': results
        }

    def _run_single_test(self, code: str, test_case: Dict[str, str]) -> Dict[str, Any]:
        """Run a single test case"""
        with self.executor as executor:
            result = executor.run_code(code, test_case['input'])

            if result.status != ExecutionStatus.SUCCESS:
                return {
                    'passed': False,
                    'status': result.status.value,
                    'error': result.error_message,
                    'runtime_ms': result.runtime_ms,
                    'memory_mb': result.memory_mb
                }

            # Compare output
            expected_output = test_case['output'].strip()
            actual_output = result.stdout.strip()

            return {
                'passed': expected_output == actual_output,
                'status': 'Success',
                'expected': expected_output,
                'actual': actual_output,
                'runtime_ms': result.runtime_ms,
                'memory_mb': result.memory_mb
            }

def format_code(code: str, language: str) -> str:
    """Format code according to language standards"""
    # TODO: Implement code formatting using language-specific formatters
    return code

def analyze_code(code: str, language: str) -> Dict[str, Any]:
    """Analyze code for potential issues and improvements"""
    # TODO: Implement static code analysis
    return {
        'warnings': [],
        'suggestions': [],
        'complexity': 'O(n)'  # Placeholder
    }