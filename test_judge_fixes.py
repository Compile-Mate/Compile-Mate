#!/usr/bin/env python3
"""
Test script to verify judge system fixes for different problem types.
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compilemate.settings')
django.setup()

from problems.models import Problem, TestCase
from judge.views import wrap_code_for_execution

def test_max_subarray():
    """Test Maximum Subarray problem."""
    print("Testing Maximum Subarray...")
    
    problem = Problem.objects.get(slug='maximum-subarray')
    test_case = TestCase.objects.filter(problem=problem, is_hidden=False).first()
    
    user_code = """
def maxSubArray(nums):
    if not nums:
        return 0
    
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum
"""
    
    starter_code = problem.starter_code.get('python', '')
    wrapped_code = wrap_code_for_execution(
        user_code, 
        'maxSubArray', 
        test_case.input_data, 
        'python', 
        True, 
        starter_code
    )
    
    print(f"Input: {test_case.input_data}")
    print(f"Expected: {test_case.expected_output}")
    print("Wrapped code:")
    print(wrapped_code)
    print("-" * 50)

def test_merge_two_lists():
    """Test Merge Two Sorted Lists problem."""
    print("Testing Merge Two Sorted Lists...")
    
    problem = Problem.objects.get(slug='merge-two-sorted-lists')
    test_case = TestCase.objects.filter(problem=problem, is_hidden=False).first()
    
    user_code = """
def mergeTwoLists(l1, l2):
    dummy = ListNode(0)
    current = dummy
    
    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next
    
    current.next = l1 if l1 else l2
    return dummy.next
"""
    
    starter_code = problem.starter_code.get('python', '')
    wrapped_code = wrap_code_for_execution(
        user_code, 
        'mergeTwoLists', 
        test_case.input_data, 
        'python', 
        True, 
        starter_code
    )
    
    print(f"Input: {test_case.input_data}")
    print(f"Expected: {test_case.expected_output}")
    print("Wrapped code:")
    print(wrapped_code)
    print("-" * 50)

def test_binary_search():
    """Test Binary Search problem."""
    print("Testing Binary Search...")
    
    problem = Problem.objects.get(slug='binary-search')
    test_case = TestCase.objects.filter(problem=problem, is_hidden=False).first()
    
    user_code = """
def searchInsert(nums, target):
    left, right = 0, len(nums)
    
    while left < right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left
"""
    
    starter_code = problem.starter_code.get('python', '')
    wrapped_code = wrap_code_for_execution(
        user_code, 
        'searchInsert', 
        test_case.input_data, 
        'python', 
        True, 
        starter_code
    )
    
    print(f"Input: {test_case.input_data}")
    print(f"Expected: {test_case.expected_output}")
    print("Wrapped code:")
    print(wrapped_code)
    print("-" * 50)

if __name__ == "__main__":
    print("Testing Judge System Fixes")
    print("=" * 50)
    
    test_max_subarray()
    test_merge_two_lists()
    test_binary_search()
    
    print("All tests completed!") 