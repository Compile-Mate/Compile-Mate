"""
CompileMate Code Execution Engine
================================
Docker-based code execution system with sandboxing and resource limits.
"""

import docker
import time
import tempfile
import os
import subprocess
from typing import Dict, Any, Optional, Tuple
from django.conf import settings


# Language configurations
LANGUAGE_CONFIG = {
    'python': {
        'image': 'compilemate-python',
        'extension': '.py',
        'compile_cmd': None,  # Python is interpreted
        'run_cmd': ['python3', '{filename}'],
        'memory_limit': '256m',
        'cpu_quota': 50000,  # 50% of one CPU core
    },
    'cpp': {
        'image': 'compilemate-cpp',
        'extension': '.cpp',
        'compile_cmd': ['g++', '-std=c++17', '-O2', '-o', '{output}', '{filename}'],
        'run_cmd': ['./{output}'],
        'memory_limit': '512m',
        'cpu_quota': 50000,
    },
    'java': {
        'image': 'compilemate-java',
        'extension': '.java',
        'compile_cmd': ['javac', '{filename}'],
        'run_cmd': ['java', '{classname}'],
        'memory_limit': '512m',
        'cpu_quota': 50000,
    },
    'javascript': {
        'image': 'compilemate-js',
        'extension': '.js',
        'compile_cmd': None,  # JavaScript is interpreted
        'run_cmd': ['node', '{filename}'],
        'memory_limit': '256m',
        'cpu_quota': 50000,
    },
}


class CodeExecutor:
    """
    Executes code in isolated Docker containers with resource limits.
    """
    
    def __init__(self, language: str, code: str):
        """
        Initialize the executor.
        
        Args:
            language: Programming language (python, cpp, java, javascript)
            code: Source code to execute
        """
        self.language = language.lower()
        self.code = code
        self.config = LANGUAGE_CONFIG.get(self.language)
        
        if not self.config:
            raise ValueError(f"Unsupported language: {language}")
        
        self.client = docker.from_env()
    
    def _create_temp_files(self) -> Tuple[str, str]:
        """
        Create temporary directory and write code to file.
        
        Returns:
            Tuple of (temp_dir_path, filename)
        """
        temp_dir = tempfile.mkdtemp()
        
        # Determine filename
        if self.language == 'java':
            # Extract class name from Java code
            classname = self._extract_java_classname()
            filename = f"{classname}{self.config['extension']}"
        else:
            filename = f"solution{self.config['extension']}"
        
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.code)
        
        return temp_dir, filename
    
    def _extract_java_classname(self) -> str:
        """Extract the public class name from Java code."""
        import re
        match = re.search(r'public\s+class\s+(\w+)', self.code)
        if match:
            return match.group(1)
        return 'Solution'  # Default class name
    
    def _compile(self, temp_dir: str, filename: str) -> Dict[str, Any]:
        """
        Compile code if compilation is needed.
        
        Args:
            temp_dir: Temporary directory containing the code
            filename: Name of the source file
            
        Returns:
            Dict with compilation result
        """
        if not self.config['compile_cmd']:
            return {'success': True, 'output': '', 'error': ''}
        
        # Prepare compile command
        output_name = 'solution'
        if self.language == 'java':
            classname = filename.replace('.java', '')
        else:
            classname = 'Solution'
        
        compile_cmd = [
            cmd.format(
                filename=f'/app/{filename}',
                output=output_name,
                classname=classname
            )
            for cmd in self.config['compile_cmd']
        ]
        
        try:
            # Run compilation in Docker container
            container = self.client.containers.run(
                self.config['image'],
                command=compile_cmd,
                volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir='/app',
                remove=False,
                detach=True,
                mem_limit=self.config['memory_limit'],
                cpu_quota=self.config['cpu_quota'],
                network_disabled=True,
            )
            
            # Wait for compilation (max 10 seconds)
            result = container.wait(timeout=10)
            logs = container.logs().decode('utf-8', errors='replace')
            
            container.remove()
            
            if result['StatusCode'] == 0:
                return {'success': True, 'output': logs, 'error': ''}
            else:
                return {'success': False, 'output': '', 'error': logs}
        
        except docker.errors.ContainerError as e:
            return {'success': False, 'output': '', 'error': str(e)}
        except Exception as e:
            return {'success': False, 'output': '', 'error': f"Compilation error: {str(e)}"}
    
    def execute(
        self,
        stdin: str = "",
        timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the code with given input.
        
        Args:
            stdin: Standard input for the program
            timeout: Execution timeout in seconds
            
        Returns:
            Dict containing execution results:
            {
                'success': bool,
                'status': str,
                'stdout': str,
                'stderr': str,
                'execution_time': float,
                'memory_used': int,
                'compile_output': str
            }
        """
        temp_dir = None
        start_time = time.time()
        
        try:
            # Create temporary files
            temp_dir, filename = self._create_temp_files()
            
            # Compile if needed
            compile_result = self._compile(temp_dir, filename)
            if not compile_result['success']:
                return {
                    'success': False,
                    'status': 'Compilation Error',
                    'stdout': '',
                    'stderr': compile_result['error'],
                    'execution_time': 0,
                    'memory_used': 0,
                    'compile_output': compile_result['error']
                }
            
            # Prepare run command
            output_name = 'solution'
            if self.language == 'java':
                classname = filename.replace('.java', '')
            else:
                classname = 'Solution'
            
            run_cmd = [
                cmd.format(
                    filename=filename,
                    output=output_name,
                    classname=classname
                )
                for cmd in self.config['run_cmd']
            ]
            
            # Handle stdin by writing to a file if provided
            if stdin:
                stdin_file = os.path.join(temp_dir, 'input.txt')
                with open(stdin_file, 'w', encoding='utf-8') as f:
                    f.write(stdin)
                # Modify run command to redirect stdin
                run_cmd = ['sh', '-c', f"{' '.join(run_cmd)} < /app/input.txt"]
            
            # Execute code in Docker container
            container = self.client.containers.run(
                self.config['image'],
                command=run_cmd,
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                working_dir='/app',
                remove=False,
                detach=True,
                mem_limit=self.config['memory_limit'],
                cpu_quota=self.config['cpu_quota'],
                network_disabled=True,
            )
            
            # Wait for execution
            try:
                result = container.wait(timeout=timeout)
                status_code = result['StatusCode']
            except Exception:
                container.kill()
                container.remove()
                return {
                    'success': False,
                    'status': 'Time Limit Exceeded',
                    'stdout': '',
                    'stderr': f'Execution timeout ({timeout}s)',
                    'execution_time': timeout,
                    'memory_used': 0,
                    'compile_output': compile_result['output']
                }
            
            # Get output
            logs = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            errors = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            # Get stats (memory usage)
            try:
                stats = container.stats(stream=False)
                memory_used = stats['memory_stats'].get('max_usage', 0)
            except Exception:
                memory_used = 0
            
            container.remove()
            
            execution_time = time.time() - start_time
            
            # Determine status
            if status_code == 0:
                status = 'Accepted'
                success = True
            elif status_code == 137:  # SIGKILL (memory limit)
                status = 'Memory Limit Exceeded'
                success = False
            else:
                status = 'Runtime Error'
                success = False
            
            return {
                'success': success,
                'status': status,
                'stdout': logs.strip(),
                'stderr': errors.strip(),
                'execution_time': round(execution_time, 3),
                'memory_used': memory_used // 1024,  # Convert to KB
                'compile_output': compile_result['output']
            }
        
        except docker.errors.ImageNotFound:
            return {
                'success': False,
                'status': 'System Error',
                'stdout': '',
                'stderr': f'Docker image not found: {self.config["image"]}',
                'execution_time': 0,
                'memory_used': 0,
                'compile_output': ''
            }
        
        except Exception as e:
            return {
                'success': False,
                'status': 'System Error',
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'execution_time': 0,
                'memory_used': 0,
                'compile_output': ''
            }
        
        finally:
            # Cleanup temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass


def execute_code(language: str, code: str, stdin: str = "", timeout: int = 5) -> Dict[str, Any]:
    """
    Convenience function to execute code.
    
    Args:
        language: Programming language
        code: Source code
        stdin: Standard input
        timeout: Timeout in seconds
        
    Returns:
        Execution results dictionary
    """
    executor = CodeExecutor(language, code)
    return executor.execute(stdin, timeout)


def execute_test_cases(
    language: str,
    code: str,
    test_cases: list,
    timeout: int = 5
) -> Dict[str, Any]:
    """
    Execute code against multiple test cases.
    
    Args:
        language: Programming language
        code: Source code
        test_cases: List of dicts with 'input' and 'expected_output' keys
        timeout: Timeout per test case in seconds
        
    Returns:
        Dict with overall results and individual test case results
    """
    executor = CodeExecutor(language, code)
    
    results = []
    passed = 0
    failed = 0
    total_time = 0
    
    for i, test_case in enumerate(test_cases):
        stdin = test_case.get('input', '')
        expected = test_case.get('expected_output', '').strip()
        
        result = executor.execute(stdin, timeout)
        actual = result['stdout'].strip()
        
        test_passed = (result['success'] and actual == expected)
        
        if test_passed:
            passed += 1
        else:
            failed += 1
        
        total_time += result['execution_time']
        
        results.append({
            'test_case': i + 1,
            'passed': test_passed,
            'status': result['status'],
            'input': stdin,
            'expected_output': expected,
            'actual_output': actual,
            'stderr': result['stderr'],
            'execution_time': result['execution_time'],
            'memory_used': result['memory_used']
        })
    
    return {
        'total_tests': len(test_cases),
        'passed': passed,
        'failed': failed,
        'total_time': round(total_time, 3),
        'results': results,
        'overall_status': 'Accepted' if failed == 0 else 'Failed'
    }

