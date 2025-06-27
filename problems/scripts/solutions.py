"""
Python Solutions for CompileMate Problems
This file contains working solutions for all sample problems in the platform.
These solutions can be used for testing the judge system and as reference implementations.
"""

# ============================================================================
# EASY PROBLEMS
# ============================================================================

def twoSum(nums, target):
    """
    Problem: Two Sum
    Difficulty: Easy
    Tags: Arrays, Hash Table
    
    Given an array of integers nums and an integer target, return indices of the two numbers 
    such that they add up to target.
    """
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


def reverseList(head):
    """
    Problem: Reverse Linked List
    Difficulty: Easy
    Tags: Linked List
    
    Given the head of a singly linked list, reverse the list, and return the reversed list.
    """
    prev = None
    current = head
    
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    
    return prev


def isValid(s):
    """
    Problem: Valid Parentheses
    Difficulty: Easy
    Tags: Stack, Strings
    
    Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', 
    determine if the input string is valid.
    """
    stack = []
    brackets = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack.pop() != brackets[char]:
                return False
    
    return len(stack) == 0


def maxProfit(prices):
    """
    Problem: Best Time to Buy and Sell Stock
    Difficulty: Easy
    Tags: Arrays, Greedy
    
    You are given an array prices where prices[i] is the price of a given stock on the ith day. 
    Find the maximum profit you can achieve.
    """
    if not prices:
        return 0
    
    min_price = prices[0]
    max_profit = 0
    
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    
    return max_profit


def mergeTwoLists(l1, l2):
    """
    Problem: Merge Two Sorted Lists
    Difficulty: Easy
    Tags: Linked List
    
    Merge two sorted linked lists and return it as a new sorted list.
    """
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


def climbStairs(n):
    """
    Problem: Climbing Stairs
    Difficulty: Easy
    Tags: Dynamic Programming
    
    You are climbing a staircase. It takes n steps to reach the top. 
    Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?
    """
    if n <= 2:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]


def searchInsert(nums, target):
    """
    Problem: Binary Search
    Difficulty: Easy
    Tags: Arrays, Binary Search
    
    Given a sorted array of n integers and a target value, return the index if the target is found. 
    If not, return the index where it would be if it were inserted in order.
    """
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


# ============================================================================
# MEDIUM PROBLEMS
# ============================================================================

def maxSubArray(nums):
    """
    Problem: Maximum Subarray
    Difficulty: Medium
    Tags: Arrays, Dynamic Programming
    
    Given an integer array nums, find the contiguous subarray (containing at least one number) 
    which has the largest sum and return its sum.
    """
    if not nums:
        return 0
    
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum


def isValidBST(root):
    """
    Problem: Validate Binary Search Tree
    Difficulty: Medium
    Tags: Tree, Binary Search
    
    Given the root of a binary tree, determine if it is a valid binary search tree (BST).
    """
    def validate(node, low=float('-inf'), high=float('inf')):
        if not node:
            return True
        
        if node.val <= low or node.val >= high:
            return False
        
        return (validate(node.left, low, node.val) and 
                validate(node.right, node.val, high))
    
    return validate(root)


def wordBreak(s, wordDict):
    """
    Problem: Word Break
    Difficulty: Medium
    Tags: Dynamic Programming, Strings
    
    Given a string s and a dictionary of strings wordDict, return true if s can be segmented 
    into a space-separated sequence of one or more dictionary words.
    """
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[n]


# ============================================================================
# HARD PROBLEMS (Additional problems for testing)
# ============================================================================

def longestConsecutive(nums):
    """
    Problem: Longest Consecutive Sequence
    Difficulty: Hard
    Tags: Array, Hash Table, Union Find
    
    Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.
    """
    if not nums:
        return 0
    
    num_set = set(nums)
    max_length = 0
    
    for num in num_set:
        if num - 1 not in num_set:  # Start of a sequence
            current_num = num
            current_length = 1
            
            while current_num + 1 in num_set:
                current_num += 1
                current_length += 1
            
            max_length = max(max_length, current_length)
    
    return max_length


def mergeKLists(lists):
    """
    Problem: Merge k Sorted Lists
    Difficulty: Hard
    Tags: Linked List, Divide and Conquer, Heap
    
    Merge k sorted linked lists and return it as one sorted list.
    """
    import heapq
    
    if not lists:
        return None
    
    # Create a min heap
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst.val, i, lst))
    
    dummy = ListNode(0)
    current = dummy
    
    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))
    
    return dummy.next


def findMedianSortedArrays(nums1, nums2):
    """
    Problem: Median of Two Sorted Arrays
    Difficulty: Hard
    Tags: Array, Binary Search, Divide and Conquer
    
    Given two sorted arrays nums1 and nums2 of size m and n respectively, 
    return the median of the two sorted arrays.
    """
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    
    while left <= right:
        partitionX = (left + right) // 2
        partitionY = (m + n + 1) // 2 - partitionX
        
        maxLeftX = float('-inf') if partitionX == 0 else nums1[partitionX - 1]
        minRightX = float('inf') if partitionX == m else nums1[partitionX]
        
        maxLeftY = float('-inf') if partitionY == 0 else nums2[partitionY - 1]
        minRightY = float('inf') if partitionY == n else nums2[partitionY]
        
        if maxLeftX <= minRightY and maxLeftY <= minRightX:
            if (m + n) % 2 == 0:
                return (max(maxLeftX, maxLeftY) + min(minRightX, minRightY)) / 2
            else:
                return max(maxLeftX, maxLeftY)
        elif maxLeftX > minRightY:
            right = partitionX - 1
        else:
            left = partitionX + 1
    
    return 0


# ============================================================================
# HELPER CLASSES FOR LINKED LIST AND TREE PROBLEMS
# ============================================================================

class ListNode:
    """Definition for singly-linked list node."""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    
    def __str__(self):
        result = []
        current = self
        while current:
            result.append(str(current.val))
            current = current.next
        return '[' + ','.join(result) + ']'


class TreeNode:
    """Definition for binary tree node."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __str__(self):
        return str(self.val)


# ============================================================================
# UTILITY FUNCTIONS FOR TESTING
# ============================================================================

def create_linked_list(values):
    """Create a linked list from a list of values."""
    if not values:
        return None
    
    head = ListNode(values[0])
    current = head
    
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    
    return head


def linked_list_to_list(head):
    """Convert a linked list to a Python list."""
    result = []
    current = head
    
    while current:
        result.append(current.val)
        current = current.next
    
    return result


def create_binary_tree(values):
    """Create a binary tree from a list of values (level-order)."""
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


def tree_to_list(root):
    """Convert a binary tree to a list (level-order)."""
    if not root:
        return []
    
    result = []
    queue = [root]
    
    while queue:
        node = queue.pop(0)
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    
    # Remove trailing None values
    while result and result[-1] is None:
        result.pop()
    
    return result


# ============================================================================
# TEST CASES FOR ALL PROBLEMS
# ============================================================================

def run_tests():
    """Run tests for all problems to verify solutions work correctly."""
    print("Running tests for all CompileMate problems...")
    
    # Test Two Sum
    assert twoSum([2, 7, 11, 15], 9) == [0, 1]
    assert twoSum([3, 2, 4], 6) == [1, 2]
    print("✓ Two Sum tests passed")
    
    # Test Reverse Linked List
    l1 = create_linked_list([1, 2, 3, 4, 5])
    reversed_l1 = reverseList(l1)
    assert linked_list_to_list(reversed_l1) == [5, 4, 3, 2, 1]
    print("✓ Reverse Linked List tests passed")
    
    # Test Valid Parentheses
    assert isValid("()") == True
    assert isValid("()[]{}") == True
    assert isValid("(]") == False
    print("✓ Valid Parentheses tests passed")
    
    # Test Best Time to Buy and Sell Stock
    assert maxProfit([7, 1, 5, 3, 6, 4]) == 5
    assert maxProfit([7, 6, 4, 3, 1]) == 0
    print("✓ Best Time to Buy and Sell Stock tests passed")
    
    # Test Merge Two Sorted Lists
    l1 = create_linked_list([1, 2, 4])
    l2 = create_linked_list([1, 3, 4])
    merged = mergeTwoLists(l1, l2)
    assert linked_list_to_list(merged) == [1, 1, 2, 3, 4, 4]
    print("✓ Merge Two Sorted Lists tests passed")
    
    # Test Climbing Stairs
    assert climbStairs(2) == 2
    assert climbStairs(3) == 3
    print("✓ Climbing Stairs tests passed")
    
    # Test Binary Search
    assert searchInsert([1, 3, 5, 6], 5) == 2
    assert searchInsert([1, 3, 5, 6], 2) == 1
    print("✓ Binary Search tests passed")
    
    # Test Maximum Subarray
    assert maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert maxSubArray([1]) == 1
    print("✓ Maximum Subarray tests passed")
    
    # Test Validate Binary Search Tree
    root1 = create_binary_tree([2, 1, 3])
    assert isValidBST(root1) == True
    root2 = create_binary_tree([5, 1, 4, None, None, 3, 6])
    assert isValidBST(root2) == False
    print("✓ Validate Binary Search Tree tests passed")
    
    # Test Word Break
    assert wordBreak("leetcode", ["leet", "code"]) == True
    assert wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]) == False
    print("✓ Word Break tests passed")
    
    # Test Longest Consecutive Sequence
    assert longestConsecutive([100, 4, 200, 1, 3, 2]) == 4
    print("✓ Longest Consecutive Sequence tests passed")
    
    print("\n🎉 All tests passed! All solutions are working correctly.")


# Standalone script to simulate an accepted submission for dashboard update
if __name__ == "__main__":
    from django.conf import settings
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compilemate.settings')
    django.setup()
    from users.models import User
    from problems.models import Problem, Submission
    from django.utils import timezone

    user = User.objects.first()  # Use the first user for demo
    problem = Problem.objects.filter(slug='two-sum').first()
    if user and problem:
        Submission.objects.create(
            user=user,
            problem=problem,
            code='def twoSum(nums, target): ...',
            language='python',
            status='accepted',
            execution_time=0.01,
            memory_used=1024,
            test_cases_passed=3,
            total_test_cases=3,
            error_message='',
            submitted_at=timezone.now(),
        )
        print(f"Created accepted submission for {user.username} on {problem.title}")
    else:
        print("User or problem not found.")

    run_tests() 