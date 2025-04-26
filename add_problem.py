import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CompileMate.settings')
django.setup()

from Home.models import Problem, ProblemSolution, TestCases

def add_problem():
    # Load problem data
    with open('problem_data.json', 'r') as f:
        data = json.load(f)
    
    # Create Problem instance
    problem = Problem(
        id=1,  # You can change this ID as needed
        name=data['name'],
        type=data['type'],
        difficuilty=data['difficulty'],
        statement=data['statement'],
        task=data['task'],
        constraints=data['constraints'],
        time_complexity="O(n)",
        space_complexity="O(n)"
    )
    problem.save()
    
    # Create ProblemSolution instance
    solution = ProblemSolution(
        problem=problem,
        python_solution=data['solutions']['python'],
        cpp_solution=data['solutions']['cpp'],
        java_solution=data['solutions']['java'],
        function_name="twoSum",
        python_template="def twoSum(nums: List[int], target: int) -> List[int]:\n    # Write your code here\n    pass",
        cpp_template="#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n    }\n};",
        java_template="class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n    }\n}"
    )
    solution.save()
    
    # Create TestCases
    for test_case in data['test_cases']:
        TestCases.objects.create(
            problem=problem,
            input=test_case['input'],
            output=test_case['output']
        )
    
    print(f"Successfully added problem: {data['name']}")

if __name__ == '__main__':
    add_problem() 