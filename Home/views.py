from time import time
from unicodedata import name
from django.shortcuts import render, HttpResponse, redirect
from Home.models import Problem, Submission, TestCases, User, Activity
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
import psutil
import json
import tempfile
import signal
from threading import Timer
from django.utils import timezone

from Home.runcode import CodeExecutor, ExecutionStatus

# Language configurations
LANGUAGE_CONFIG = {
    'cpp': {
        'extension': '.cpp',
        'compile_cmd': ['g++', '-std=c++17', '-O2', '-Wall'],
        'run_cmd': './a.out',
        'time_limit': 2,  # seconds
        'memory_limit': 512  # MB
    },
    'java': {
        'extension': '.java',
        'compile_cmd': ['javac'],
        'run_cmd': ['java'],
        'time_limit': 3,
        'memory_limit': 512
    },
    'python': {
        'extension': '.py',
        'compile_cmd': None,
        'run_cmd': ['python3'],
        'time_limit': 5,
        'memory_limit': 512
    }
}

def get_memory_usage(pid):
    """Get memory usage of a process in MB"""
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss / 1024 / 1024
    except:
        return 0

def run_with_timeout(cmd, input_data=None, timeout=2):
    """Run a command with timeout and input"""
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if input_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        timer = Timer(timeout, lambda p: p.kill(), [process])
        timer.start()
        
        stdout, stderr = process.communicate(input=input_data)
        timer.cancel()
        
        memory_used = get_memory_usage(process.pid)
        return process.returncode, stdout, stderr, memory_used
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Time Limit Exceeded", 0
    except Exception as e:
        return -1, "", str(e), 0

@csrf_exempt
def run_code(request):
    """Handle code execution requests"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'cpp')
        input_data = data.get('input', '')
        
        if not code:
            return JsonResponse({'status': 'error', 'error': 'No code provided'})
        
        # Create CodeExecutor instance
        with CodeExecutor(language) as executor:
            result = executor.run_code(code, input_data)
            
            if result.status == ExecutionStatus.SUCCESS:
                return JsonResponse({
                    'status': 'success',
                    'output': result.stdout,
                    'memory_used': result.memory_mb,
                    'runtime': result.runtime_ms
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': result.error_message,
                    'memory_used': result.memory_mb,
                    'runtime': result.runtime_ms
                })
                
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)})

@csrf_exempt
def submit_code(request, user_name, problem_id):
    """Handle code submission"""
    if request.method == 'POST':
        try:
            # Get the problem and code from the request
            problem = Problem.objects.get(id=problem_id)
            code = request.POST.get('code', '')
            language = request.POST.get('language', 'python')
            
            # Initialize variables
            verdict = 'Wrong Answer'
            error_message = None
            failed_case = None
            total_runtime = 0
            max_memory = 0
            all_passed = True
            
            # Get all test cases for the problem
            test_cases = TestCases.objects.filter(problem=problem)
            
            # Create a code executor
            executor = CodeExecutor(code, language)
            
            # Run each test case
            for test_case in test_cases:
                result = executor.run(test_case.input_data)
                
                if result.status == ExecutionStatus.SUCCESS:
                    # Compare output
                    if result.output.strip() == test_case.output_data.strip():
                        total_runtime = max(total_runtime, result.runtime)
                        max_memory = max(max_memory, result.memory_usage)
                    else:
                        all_passed = False
                        verdict = 'Wrong Answer'
                        failed_case = {
                            'input': test_case.input_data,
                            'expected': test_case.output_data,
                            'actual': result.output
                        }
                        break
                else:
                    all_passed = False
                    verdict = result.status.value
                    error_message = result.error
                    break
            
            if all_passed:
                verdict = 'Accepted'
            
            # Create submission record
            submission = Submission(
                user=User.objects.get(username=user_name),
                problem=problem,
                code=code,
                verdict=verdict,
                time=datetime.now()
            )
            submission.save()
            
            # Create activity entry for the submission
            activity_title = f"Submitted solution to {problem.name}"
            activity_desc = f"Verdict: {verdict}"
            if verdict == 'Accepted':
                activity_desc += " 🎉"
            
            Activity.objects.create(
                user=submission.user,
                type='submission',
                title=activity_title,
                description=activity_desc
            )
            
            # Update user's solved problems if all test cases passed
            if all_passed:
                user = User.objects.get(username=user_name)
                # Only increment problems_solved if this is the first accepted solution
                if not Submission.objects.filter(
                    user=user,
                    problem=problem,
                    verdict='Accepted'
                ).exists():
                    user.problems_solved += 1
                    user.save()
                    
                    # Create achievement activity for first solve
                    Activity.objects.create(
                        user=user,
                        type='achievement',
                        title=f"First solve of {problem.name}!",
                        description=f"Successfully solved {problem.name} for the first time 🏆"
                    )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'All test cases passed!',
                    'runtime': total_runtime,
                    'memory': max_memory
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': error_message,
                    'failed_test_case': failed_case,
                    'runtime': total_runtime,
                    'memory': max_memory
                })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': f'Internal Error: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'error': 'Invalid request method'
    })

def start(request):
    return render(request,'startpage.html')

def home(request, user_name):
    user = User.objects.get(username=str(user_name))
    types = Problem.objects.values('type').distinct()
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    
    # Get recent activities for the user
    recent_activities = Activity.objects.filter(user=user).order_by('-time')[:5]
    
    # Get user's streak (number of consecutive days with accepted submissions)
    streak = 0
    last_submission = Submission.objects.filter(user=user, verdict='Accepted').order_by('-time').first()
    if last_submission:
        current_date = timezone.now().date()
        submission_date = last_submission.time.date()
        if current_date == submission_date:
            # Count consecutive days backwards from today
            temp_date = current_date
            while True:
                if Submission.objects.filter(
                    user=user,
                    verdict='Accepted',
                    time__date=temp_date
                ).exists():
                    streak += 1
                    temp_date = temp_date - timezone.timedelta(days=1)
                else:
                    break
    
    return render(request, 'homepage.html', {
        'user': user,
        'types': types,
        'rank': rank,
        'recent_activities': recent_activities,
        'streak': streak,
        'problems_solved': user.problems_solved
    })

def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                # Store user info in session
                request.session['user_id'] = user.username
                request.session['user_email'] = user.email
                request.session['user_name'] = user.name
                
                types = Problem.objects.values('type').distinct()
                return render(request, 'homepage.html', {'user': user, 'types': types})
            else:
                messages.error(request, 'Incorrect Password')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    
    return render(request, 'startpage.html')

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords don\'t match.')
            return render(request, 'signup.html')
            
        # Hash the password before saving
        hashed_password = make_password(password1)
        
        try:
            user = User(name=name, username=username, email=email, password=hashed_password)
            user.save()
            messages.success(request, 'Your Account has been created.')
            return redirect('signin')
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            
    return render(request, 'signup.html')

def logout(request):
    # Clear all session data
    request.session.flush()
    return redirect('start')

# views.py

def problems(request, user_name=None):
    user = None
    rank = None

    if user_name is not None:
        try:
            user = User.objects.get(username=str(user_name))
            rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
        except User.DoesNotExist:
            pass

    problems = Problem.objects.all()
    types = Problem.objects.values('type').distinct()
    return render(request, 'problems.html', {'user': user, 'problems': problems, 'types': types, 'rank': rank})





def problem_search(request,user_name):
    if request.method == "POST":
        search_string = request.POST.get('search')
        problems = Problem.objects.filter(name__icontains=search_string)
    else:
        problems = Problem.objects.all()
    user = User.objects.get(username=str(user_name))
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    types = Problem.objects.values('type').distinct()
    return render(request,'problems.html',{'user':user,'problems':problems,'types':types,'rank':rank})

def problems_typeSpecific(request,user_name,type):
    user = User.objects.get(username=str(user_name))
    problems = Problem.objects.filter(type=str(type))
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    types = Problem.objects.values('type').distinct()
    return render(request,'problems.html',{'user':user,'problems':problems,'types':types,'rank':rank})

def problems_difficuiltySpecific(request,user_name,difficuilty):
    user = User.objects.get(username=str(user_name))
    problems = Problem.objects.filter(difficuilty=str(difficuilty))
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    types = Problem.objects.values('type').distinct()
    return render(request,'problems.html',{'user':user,'problems':problems,'types':types,'rank':rank})

def problem_description(request, user_name, id):
    user = User.objects.get(username=str(user_name))
    problem = Problem.objects.get(id=id)
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1

    # Get constraints list using the model's helper method
    problem.constraints = problem.get_constraints()

    # Get language-specific templates
    templates = {
        'python': '',
        'cpp': '',
        'java': ''
    }
    
    try:
        problem_solution = problem.solution
        for lang in templates.keys():
            template = problem_solution.get_template(lang)
            if template:
                templates[lang] = template
            else:
                # Default templates if none are stored
                if lang == 'python':
                    templates[lang] = f"def {problem_solution.function_name}():\n    # Write your code here\n    pass"
                elif lang == 'cpp':
                    templates[lang] = f"class Solution {{\npublic:\n    // Write your code here\n}};"
                elif lang == 'java':
                    templates[lang] = f"public class Solution {{\n    // Write your code here\n}}"
    except:
        # Use default templates if no solution exists
        templates = {
            'python': "def solution():\n    # Write your code here\n    pass",
            'cpp': "class Solution {\npublic:\n    // Write your code here\n};",
            'java': "public class Solution {\n    // Write your code here\n}"
        }
    
    return render(request, 'problem_desc.html', {
        'user': user,
        'problem': problem,
        'rank': rank,
        'templates': templates
    })

def submit(request, user_name, id):
    user = User.objects.get(username=str(user_name))
    problem = Problem.objects.get(id=id)
    test_cases = TestCases.objects.filter(problem=problem)
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    
    if request.method == 'POST':
        code = request.POST.get('textarea')
        lang_code = request.POST.get('language')
        verdict = "Internal Error"
        error = ""

        # Updated language mapping to match frontend values
        language_map = {'cpp': "cpp", 'java': "java", 'python': "python"}
        
        if lang_code not in language_map:
            return render(request, 'problem_desc.html', {
                'user': user,
                'problem': problem,
                'rank': rank,
                'error': "Invalid language selected"
            })

        try:
            # Create CodeExecutor instance
            with CodeExecutor(language_map[lang_code]) as executor:
                all_passed = True
                failed_test_case = 0
                
                # Run each test case
                for i, test_case in enumerate(test_cases, 1):
                    result = executor.run_code(code, test_case.input)
                    
                    if result.status != ExecutionStatus.SUCCESS:
                        verdict = f"{result.status.value} on test case {i}"
                        error = result.error_message
                        all_passed = False
                        failed_test_case = i
                        break
                    
                    # Compare output
                    expected_output = test_case.output.strip()
                    actual_output = result.stdout.strip()
                    
                    if expected_output != actual_output:
                        verdict = f"Wrong Answer on test case {i}"
                        all_passed = False
                        failed_test_case = i
                        break
                
                if all_passed:
                    verdict = "Accepted"
                    # Update user's solved problems if not already solved
                    if not Submission.objects.filter(
                        user=user,
                        problem=problem,
                        verdict='Accepted'
                    ).exists():
                        user.problems_solved += 1
                        user.save()

            # Save submission
            submission = Submission(
                user=user,
                problem=problem,
                code=code,
                verdict=verdict,
                time=datetime.now()
            )
            submission.save()
            
            return render(request, 'problem_desc.html', {
                'user': user,
                'problem': problem,
                'rank': rank,
                'verdict': verdict,
                'error': error,
                'test_case_failed': failed_test_case if not all_passed else 0
            })
            
        except Exception as e:
            error = str(e)
            return render(request, 'problem_desc.html', {
                'user': user,
                'problem': problem,
                'rank': rank,
                'error': f"Error executing code: {error}"
            })
    
    return render(request, 'problem_desc.html', {
        'user': user,
        'problem': problem,
        'rank': rank
    })

def submissions(request,user_name):
    user = User.objects.get(username=str(user_name))
    submissions = Submission.objects.filter(user=user).order_by('-time')
    rank = User.objects.all().filter(problems_solved__gt=user.problems_solved).count() + 1
    return render(request,'submissions.html',{'user':user,'submissions':submissions,'rank':rank})

def leaderboard(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('start')
        
    # Get all users sorted by problems_solved in descending order
    users = User.objects.all().order_by('-problems_solved', 'username')  # Secondary sort by username for consistent ordering
    current_user = User.objects.get(username=request.session['user_id'])
    
    return render(request, 'leaderboard.html', {
        'user': users,
        'current_user': current_user
    })

# Create default admin user
def create_admin():
    try:
        admin = User.objects.create(
            username="admin",
            name="Administrator",
            email="admin@compilemate.com",
            password="admin123",  # This is a default password, should be changed after first login
            problems_solved=0
        )
        return "Admin user created successfully"
    except Exception as e:
        return f"Error creating admin user: {str(e)}"