import requests
import time
import re
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from problems.models import Problem, TestCase, Submission
from users.models import User
from django.utils import timezone
import ast

# Judge0 public API endpoint
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"
JUDGE0_SUBMIT = f"{JUDGE0_URL}/submissions/?base64_encoded=false&wait=false"
JUDGE0_GET = f"{JUDGE0_URL}/submissions/{{token}}?base64_encoded=false"
JUDGE0_HEADERS = {
    'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com',
    'X-RapidAPI-Key': '09972a180emsh10e4d57740810a2p1d1d20jsnfd2d9841d196',
    'Content-Type': 'application/json',
}

# Map your language names to Judge0 IDs
LANGUAGE_MAP = {
    'python': 71,      # Python 3
    'cpp': 54,         # C++ (GCC 9.2.0)
    'java': 62,        # Java (OpenJDK 13.0.1)
    'javascript': 63,  # JavaScript (Node.js 12.14.0)
}

def extract_function_name(starter_code, language):
    """Extract function name from starter code."""
    if language == 'python':
        # Look for def function_name(
        match = re.search(r'def\s+(\w+)\s*\(', starter_code)
        return match.group(1) if match else None
    elif language == 'cpp':
        # Look for function_name(
        match = re.search(r'(\w+)\s*\([^)]*\)\s*{', starter_code)
        return match.group(1) if match else None
    elif language == 'java':
        # Look for public static function_name(
        match = re.search(r'public\s+(?:static\s+)?(\w+)\s+(\w+)\s*\(', starter_code)
        return match.group(2) if match else None
    elif language == 'javascript':
        # Look for function function_name(
        match = re.search(r'function\s+(\w+)\s*\(', starter_code)
        return match.group(1) if match else None
    return None

def parse_test_input(input_data, function_name, language, starter_code=None):
    lines = [line.strip() for line in input_data.strip().split('\n') if line.strip()]
    args = []
    if language == 'python' and starter_code:
        match = re.search(r'def\s+\w+\s*\(([^)]*)\)', starter_code)
        arg_names = [arg.strip().split('=')[0] for arg in match.group(1).split(',')] if match else []
        num_args = len(arg_names)
        # If only one line and two arguments, treat all but last value as a list for the first argument
        if len(lines) == 1 and num_args == 2:
            values = lines[0].split()
            first_arg = [int(x) if x.lstrip('-').isdigit() else float(x) if '.' in x else x for x in values[:-1]]
            last_val = values[-1]
            try:
                second_arg = int(last_val)
            except Exception:
                try:
                    second_arg = float(last_val)
                except Exception:
                    second_arg = last_val
            args = [str(first_arg), second_arg]
            return args
        # Otherwise, treat each line as an argument
        for i, arg in enumerate(arg_names):
            if i >= len(lines):
                args.append('None')
                continue
            line = lines[i]
            if ' ' in line:
                try:
                    vals = [int(x) if x.lstrip('-').isdigit() else float(x) if '.' in x else x for x in line.split()]
                    if all(isinstance(v, (int, float)) for v in vals):
                        args.append(str(vals))
                    else:
                        args.append(f"[{', '.join([repr(v) for v in vals])}]")
                except Exception:
                    args.append(f"[{', '.join([repr(x) for x in line.split()])}]")
            else:
                try:
                    args.append(int(line))
                except Exception:
                    try:
                        args.append(float(line))
                    except Exception:
                        args.append(repr(line))
        return args
    for line in lines:
        args.append(repr(line))
    return args

def wrap_code_for_execution(user_code, function_name, test_input, language, is_submission=False, starter_code=None):
    """Generic wrapper for any function/problem, dynamic input parsing and output formatting."""
    if not function_name:
        return user_code
    if language == 'python':
        if is_submission:
            # Extract argument names from the starter code
            arg_names = []
            if starter_code:
                match = re.search(r'def\s+\w+\s*\(([^)]*)\)', starter_code)
                if match:
                    arg_names = [arg.strip().split('=')[0] for arg in match.group(1).split(',') if arg.strip()]
            
            # Check if this is a linked list problem
            is_linked_list_problem = (
                any('ListNode' in starter_code for lang in ['cpp', 'java']) or 
                any(arg in arg_names for arg in ['head', 'l1', 'l2']) or
                'mergeTwoLists' in function_name or 'reverseList' in function_name
            )
            is_tree_problem = (
                any('TreeNode' in starter_code for lang in ['cpp', 'java']) or 
                'root' in arg_names or
                'isValidBST' in function_name
            )
            
            # Parse each input line as int, float, list, or str
            lines = [line.strip() for line in test_input.strip().split('\n') if line.strip()]
            args = []
            
            if is_linked_list_problem and len(lines) >= 2:
                # Handle linked list problems
                linked_list_helpers = '''
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def create_linked_list(values):
    if not values:
        return None
    head = ListNode(values[0])
    current = head
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

def linked_list_to_list(head):
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result
'''
                
                if len(lines) >= 4 and len(arg_names) == 2:
                    # Two linked lists (e.g., mergeTwoLists)
                    list1_values = [int(x) for x in lines[0].split()]
                    list1_length = int(lines[1])
                    list2_values = [int(x) for x in lines[2].split()]
                    list2_length = int(lines[3])
                    
                    list1 = f"create_linked_list({list1_values})"
                    list2 = f"create_linked_list({list2_values})"
                    args = [list1, list2]
                else:
                    # Single linked list (e.g., reverseList)
                    list_values = [int(x) for x in lines[0].split()]
                    list_length = int(lines[1]) if len(lines) > 1 else len(list_values)
                    
                    list_head = f"create_linked_list({list_values})"
                    args = [list_head]
                
                args_str = ', '.join(args)
                
                return f'''{linked_list_helpers}

{user_code}

if __name__ == '__main__':
    result = {function_name}({args_str})
    if result:
        output = linked_list_to_list(result)
        print(' '.join(map(str, output)))
    else:
        print('')
'''
            elif is_tree_problem and len(lines) >= 2:
                # Handle tree problems
                tree_helpers = '''
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def create_binary_tree(values):
    if not values:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root
'''
                
                # Parse tree values (replace 'null' with None)
                tree_values = []
                for val in lines[0].split():
                    if val.lower() == 'null':
                        tree_values.append(None)
                    else:
                        tree_values.append(int(val))
                
                tree_length = int(lines[1]) if len(lines) > 1 else len(tree_values)
                tree_root = f"create_binary_tree({tree_values})"
                args = [tree_root]
                args_str = ', '.join(args)
                
                return f'''{tree_helpers}

{user_code}

if __name__ == '__main__':
    result = {function_name}({args_str})
    if isinstance(result, bool):
        print(str(result).lower())
    else:
        print(result)
'''
            else:
                # Regular problem parsing
                for line in lines:
                    try:
                        val = ast.literal_eval(line)
                    except Exception:
                        # Try to parse as space-separated ints/floats
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                val = [ast.literal_eval(x) for x in parts]
                            except Exception:
                                val = parts
                        else:
                            val = line
                    args.append(val)
                # If number of args doesn't match, try to flatten
                if len(args) > len(arg_names) and len(arg_names) == 2 and isinstance(args[0], list):
                    # e.g. twoSum: [2,7,11,15], 9
                    args = [args[0], args[-1]]
                args_str = ', '.join(repr(a) for a in args)
                return f'''{user_code}

if __name__ == '__main__':
    import ast
    result = {function_name}({args_str})
    if isinstance(result, list):
        print(' '.join(map(str, result)))
    elif isinstance(result, bool):
        print(str(result).lower())
    elif result is None:
        print('')
    else:
        print(result)
'''
        else:
            # Run Code mode - similar logic, but reads from stdin
            return f"{user_code}\n\nif __name__ == '__main__':\n    import sys, ast\n    input_data = sys.stdin.read().strip()\n    if input_data:\n        lines = input_data.split('\\n')\n        args = []\n        for line in lines:\n            line = line.strip()\n            if not line:\n                continue\n            try:\n                val = ast.literal_eval(line)\n            except Exception:\n                parts = line.split()\n                if len(parts) > 1:\n                    try:\n                        val = [ast.literal_eval(x) for x in parts]\n                    except Exception:\n                        val = parts\n                else:\n                    val = line\n            args.append(val)\n        result = {function_name}(*args)\n        if isinstance(result, list):\n            print(' '.join(map(str, result)))\n        elif isinstance(result, bool):\n            print(str(result).lower())\n        elif result is None:\n            print('')\n        else:\n            print(result)"
    elif language == 'cpp':
        if is_submission:
            args = parse_test_input(test_input, function_name, language)
            args_str = ', '.join(str(arg) for arg in args)
            return f"{user_code}\n\nint main() {{\n    auto result = {function_name}({args_str});\n    std::cout << result << std::endl;\n    return 0;\n}}"
        else:
            return f"{user_code}\n\nint main() {{\n    std::string line;\n    std::vector<std::string> inputs;\n    while (std::getline(std::cin, line)) {{\n        inputs.push_back(line);\n    }}\n    // Parse inputs and call function\n    // This is a simplified version - you might need more complex parsing\n    return 0;\n}}"
    elif language == 'java':
        if is_submission:
            args = parse_test_input(test_input, function_name, language)
            args_str = ', '.join(str(arg) for arg in args)
            return f"{user_code}\n\npublic class Main {{\n    public static void main(String[] args) {{\n        Solution solution = new Solution();\n        Object result = solution.{function_name}({args_str});\n        System.out.println(result);\n    }}\n}}"
        else:
            return f"{user_code}\n\npublic class Main {{\n    public static void main(String[] args) {{\n        Solution solution = new Solution();\n        // Parse input and call function\n    }}\n}}"
    elif language == 'javascript':
        if is_submission:
            args = parse_test_input(test_input, function_name, language)
            args_str = ', '.join(str(arg) for arg in args)
            return f"{user_code}\n\nconst result = {function_name}({args_str});\nif (Array.isArray(result)) {{\n    console.log(result.join(' '));\n}} else if (typeof result === 'boolean') {{\n    console.log(result.toString().toLowerCase());\n}} else if (result === null || result === undefined) {{\n    console.log('');\n}} else {{\n    console.log(result);\n}}"
        else:
            return f"{user_code}\n\n// Read input from stdin\nconst readline = require('readline');\nconst rl = readline.createInterface({{input: process.stdin, output: process.stdout}});\nlet input = [];\nrl.on('line', (line) => {{input.push(line);}});\nrl.on('close', () => {{\n    // Parse input and call function\n    const result = {function_name}(...input);\n    if (Array.isArray(result)) {{\n        console.log(result.join(' '));\n    }} else if (typeof result === 'boolean') {{\n        console.log(result.toString().toLowerCase());\n    }} else if (result === null || result === undefined) {{\n        console.log('');\n    }} else {{\n        console.log(result);\n    }}\n}});"
    return user_code

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SubmitCodeView(View):
    def post(self, request, *args, **kwargs):
        print("POST data:", request.POST)
        code = request.POST.get('code')
        language = request.POST.get('language')
        problem_id = request.POST.get('problem_id')
        run_mode = request.POST.get('run_mode', 'submit')  # 'run' or 'submit'
        custom_input = request.POST.get('input', '')  # For Run Code
        
        user = request.user
        
        if not code or not language:
            return JsonResponse({'error': 'Missing code or language'}, status=400)
        
        lang_id = LANGUAGE_MAP.get(language)
        if not lang_id:
            return JsonResponse({'error': 'Unsupported language'}, status=400)
        
        # Check if this is a Run Code request or Submit Solution
        is_run_code = run_mode == 'run'
        
        if is_run_code:
            # Run Code with sample test cases (like LeetCode)
            if not problem_id:
                return JsonResponse({'error': 'Problem ID required for Run Code'}, status=400)
                
            problem = Problem.objects.filter(id=problem_id, status='published').first()
            if not problem:
                return JsonResponse({'error': 'Problem not found'}, status=404)
            
            # Extract function name from starter code
            starter_code = problem.starter_code.get(language, '')
            function_name = extract_function_name(starter_code, language)
            
            # Use sample test cases (non-hidden) for Run Code
            sample_test_cases = TestCase.objects.filter(problem=problem, is_hidden=False).order_by('order')[:2]  # Use first 2 sample cases
            
            if not sample_test_cases.exists():
                return JsonResponse({'error': 'No sample test cases available'}, status=404)
            
            test_case_results = []
            max_time = 0
            max_memory = 0
            
            for tc in sample_test_cases:
                # Wrap code for this test case
                wrapped_code = wrap_code_for_execution(code, function_name, tc.input_data, language, True, starter_code=starter_code)
                
                payload = {
                    'source_code': wrapped_code,
                    'language_id': lang_id,
                    'stdin': '',  # Input is now in the code
                }
                
                try:
                    submit_resp = requests.post(JUDGE0_SUBMIT, json=payload, headers=JUDGE0_HEADERS)
                    if submit_resp.status_code != 201:
                        return JsonResponse({'error': 'Judge0 submission failed'}, status=500)
                    
                    token = submit_resp.json().get('token')
                    
                    # Poll for results
                    for _ in range(20):
                        result_resp = requests.get(JUDGE0_GET.format(token=token), headers=JUDGE0_HEADERS)
                        result = result_resp.json()
                        if result.get('status', {}).get('id') in [3, 6, 11]:
                            break
                        time.sleep(0.5)
                    
                    output = (result.get('stdout') or '').strip()
                    expected = (tc.expected_output or '').strip()
                    
                    # Normalize output for comparison
                    if output.lower() in ['true', 'false']:
                        output = output.lower()
                    if expected.lower() in ['true', 'false']:
                        expected = expected.lower()
                    
                    status = 'passed' if output == expected else 'failed'
                    
                    test_case_results.append({
                        'input': tc.input_data,
                        'expected': expected,
                        'output': output,
                        'status': status,
                        'error_message': result.get('stderr') or result.get('compile_output') or '',
                    })
                    
                    if result.get('time') and float(result['time']) > max_time:
                        max_time = float(result['time'])
                    if result.get('memory') and int(result['memory']) > max_memory:
                        max_memory = int(result['memory'])
                        
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            
            return JsonResponse({
                'status': 'Run Code',
                'test_cases': test_case_results,
                'execution_time': max_time,
                'memory_used': max_memory,
                'message': 'Sample test cases executed successfully'
            })
        
        else:
            # Submit Solution - auto-grading
            problem = Problem.objects.filter(id=problem_id, status='published').first()
            if not problem:
                return JsonResponse({'error': 'Problem not found'}, status=404)
            
            # Extract function name from starter code
            starter_code = problem.starter_code.get(language, '')
            function_name = extract_function_name(starter_code, language)
            
            test_cases = TestCase.objects.filter(problem=problem).order_by('order')
            total = test_cases.count()
            passed = 0
            failed_case = None
            error_message = ''
            test_case_results = []
            max_time = 0
            max_memory = 0
            
            for tc in test_cases:
                # Wrap code for this test case
                wrapped_code = wrap_code_for_execution(code, function_name, tc.input_data, language, True, starter_code=starter_code)
                
                payload = {
                    'source_code': wrapped_code,
                    'language_id': lang_id,
                    'stdin': '',  # Input is now in the code
                }
                
                try:
                    submit_resp = requests.post(JUDGE0_SUBMIT, json=payload, headers=JUDGE0_HEADERS)
                    if submit_resp.status_code != 201:
                        error_message = 'Judge0 submission failed'
                        break
                    
                    token = submit_resp.json().get('token')
                    
                    # Poll for results
                    for _ in range(20):
                        result_resp = requests.get(JUDGE0_GET.format(token=token), headers=JUDGE0_HEADERS)
                        result = result_resp.json()
                        if result.get('status', {}).get('id') in [3, 6, 11]:
                            break
                        time.sleep(0.5)
                    
                    output = (result.get('stdout') or '').strip()
                    expected = (tc.expected_output or '').strip()
                    
                    # Normalize output for comparison
                    if output.lower() in ['true', 'false']:
                        output = output.lower()
                    if expected.lower() in ['true', 'false']:
                        expected = expected.lower()
                    
                    status = 'passed' if output == expected else 'failed'
                    
                    if status == 'passed':
                        passed += 1
                    else:
                        failed_case = tc
                        error_message = f"Expected: {expected}, Got: {output}"
                    
                    test_case_results.append({
                        'input': tc.input_data,
                        'expected': expected,
                        'output': output,
                        'status': status,
                        'error_message': result.get('stderr') or result.get('compile_output') or error_message,
                    })
                    
                    if result.get('time') and float(result['time']) > max_time:
                        max_time = float(result['time'])
                    if result.get('memory') and int(result['memory']) > max_memory:
                        max_memory = int(result['memory'])
                    
                    if status == 'failed':
                        break  # Stop on first failure
                        
                except Exception as e:
                    error_message = str(e)
                    break
            
            # Determine submission status
            if passed == total:
                submission_status = 'accepted'
            elif error_message:
                submission_status = 'runtime_error'
            else:
                submission_status = 'wrong_answer'
            
            # Save submission
            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=code,
                language=language,
                status=submission_status,
                execution_time=max_time,
                memory_used=max_memory,
                test_cases_passed=passed,
                total_test_cases=total,
                error_message=error_message,
                failed_test_case=failed_case,
            )
            
            # Update user stats if first accepted
            if submission_status == 'accepted' and submission.is_first_accepted:
                user.coins += problem.coin_reward
                user.xp += problem.xp_reward
                user.problems_solved += 1
                user.save()
                problem.accepted_submissions += 1
                problem.save()
            
            problem.total_submissions += 1
            problem.save()
            
            return JsonResponse({
                'status': submission.status.title().replace('_', ' '),
                'test_cases': test_case_results,
                'execution_time': max_time,
                'memory_used': max_memory,
                'error_message': error_message,
                'submission_id': submission.id,
            })