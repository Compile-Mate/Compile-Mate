from django.core.management.base import BaseCommand
from problems.models import Problem, Tag, TestCase
from users.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Add 10 sample LeetCode-style problems with tags, constraints, examples, starter code, and test cases.'

    def handle(self, *args, **kwargs):
        TAGS = [
            ("Arrays", "Problems involving arrays", "#3B82F6"),
            ("Strings", "Problems involving strings", "#F59E42"),
            ("Hash Table", "Problems involving hash tables", "#10B981"),
            ("Math", "Mathematical problems", "#F59E0B"),
            ("Dynamic Programming", "DP problems", "#8B5CF6"),
            ("Linked List", "Problems involving linked lists", "#EF4444"),
            ("Stack", "Problems involving stacks", "#F97316"),
            ("Tree", "Problems involving trees", "#22D3EE"),
            ("Binary Search", "Problems involving binary search", "#6366F1"),
            ("Greedy", "Greedy algorithms", "#EAB308"),
            # Added for new problems:
            ("Two Pointers", "Problems using the two pointers technique", "#A21CAF"),
            ("DFS", "Depth-First Search problems", "#0EA5E9"),
            ("BFS", "Breadth-First Search problems", "#F43F5E"),
            ("Backtracking", "Backtracking problems", "#F59E42"),
        ]
        tag_objs = {}
        for name, desc, color in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={"description": desc, "color": color})
            tag_objs[name] = tag

        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No user found to assign as problem creator.'))
            return

        problems_data = [
            {
                "title": "Two Sum",
                "slug": "two-sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nOnly one valid answer exists.",
                "examples": [
                    {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
                    {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"},
                ],
                "starter_code": {
                    "python": "def twoSum(nums, target):\n    # Write your code here\n    pass",
                    "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    // Write your code here\n}",
                    "java": "public int[] twoSum(int[] nums, int target) {\n    // Write your code here\n}",
                    "javascript": "function twoSum(nums, target) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Hash Table"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "2 7 11 15\n4\n9", "expected_output": "0 1", "is_hidden": False},
                    {"input_data": "3 2 4\n3\n6", "expected_output": "1 2", "is_hidden": False},
                    {"input_data": "1 2 3 4 5\n5\n9", "expected_output": "3 4", "is_hidden": True},
                ]
            },
            {
                "title": "Reverse Linked List",
                "slug": "reverse-linked-list",
                "description": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "The number of nodes in the list is the range [0, 5000].\n-5000 <= Node.val <= 5000",
                "examples": [
                    {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"},
                    {"input": "head = [1,2]", "output": "[2,1]"},
                ],
                "starter_code": {
                    "python": "def reverseList(head):\n    # Write your code here\n    pass",
                    "cpp": "ListNode* reverseList(ListNode* head) {\n    // Write your code here\n}",
                    "java": "public ListNode reverseList(ListNode head) {\n    // Write your code here\n}",
                    "javascript": "function reverseList(head) {\n    // Write your code here\n}"
                },
                "tags": ["Linked List"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 2 3 4 5\n5", "expected_output": "5 4 3 2 1", "is_hidden": False},
                    {"input_data": "1 2\n2", "expected_output": "2 1", "is_hidden": False},
                    {"input_data": "", "expected_output": "", "is_hidden": True},
                ]
            },
            {
                "title": "Valid Parentheses",
                "slug": "valid-parentheses",
                "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= s.length <= 10^4",
                "examples": [
                    {"input": "s = '()'", "output": "true"},
                    {"input": "s = '()[]{}'", "output": "true"},
                    {"input": "s = '(]'", "output": "false"},
                ],
                "starter_code": {
                    "python": "def isValid(s):\n    # Write your code here\n    pass",
                    "cpp": "bool isValid(string s) {\n    // Write your code here\n}",
                    "java": "public boolean isValid(String s) {\n    // Write your code here\n}",
                    "javascript": "function isValid(s) {\n    // Write your code here\n}"
                },
                "tags": ["Stack", "Strings"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "()", "expected_output": "true", "is_hidden": False},
                    {"input_data": "()[]{}", "expected_output": "true", "is_hidden": False},
                    {"input_data": "(]", "expected_output": "false", "is_hidden": True},
                ]
            },
            {
                "title": "Best Time to Buy and Sell Stock",
                "slug": "best-time-to-buy-and-sell-stock",
                "description": "You are given an array prices where prices[i] is the price of a given stock on the ith day. Find the maximum profit you can achieve.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= prices.length <= 10^5\n0 <= prices[i] <= 10^4",
                "examples": [
                    {"input": "prices = [7,1,5,3,6,4]", "output": "5"},
                    {"input": "prices = [7,6,4,3,1]", "output": "0"},
                ],
                "starter_code": {
                    "python": "def maxProfit(prices):\n    # Write your code here\n    pass",
                    "cpp": "int maxProfit(vector<int>& prices) {\n    // Write your code here\n}",
                    "java": "public int maxProfit(int[] prices) {\n    // Write your code here\n}",
                    "javascript": "function maxProfit(prices) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Greedy"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "7 1 5 3 6 4\n6", "expected_output": "5", "is_hidden": False},
                    {"input_data": "7 6 4 3 1\n5", "expected_output": "0", "is_hidden": False},
                ]
            },
            {
                "title": "Maximum Subarray",
                "slug": "maximum-subarray",
                "description": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
                "examples": [
                    {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6"},
                    {"input": "nums = [1]", "output": "1"},
                ],
                "starter_code": {
                    "python": "def maxSubArray(nums):\n    # Write your code here\n    pass",
                    "cpp": "int maxSubArray(vector<int>& nums) {\n    // Write your code here\n}",
                    "java": "public int maxSubArray(int[] nums) {\n    // Write your code here\n}",
                    "javascript": "function maxSubArray(nums) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Dynamic Programming"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6", "is_hidden": False},
                    {"input_data": "1", "expected_output": "1", "is_hidden": False},
                ]
            },
            {
                "title": "Merge Two Sorted Lists",
                "slug": "merge-two-sorted-lists",
                "description": "Merge two sorted linked lists and return it as a new sorted list.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "The number of nodes in both lists is in the range [0, 50].\n-100 <= Node.val <= 100",
                "examples": [
                    {"input": "l1 = [1,2,4], l2 = [1,3,4]", "output": "[1,1,2,3,4,4]"},
                    {"input": "l1 = [], l2 = []", "output": "[]"},
                ],
                "starter_code": {
                    "python": "def mergeTwoLists(l1, l2):\n    # Write your code here\n    pass",
                    "cpp": "ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {\n    // Write your code here\n}",
                    "java": "public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n    // Write your code here\n}",
                    "javascript": "function mergeTwoLists(l1, l2) {\n    // Write your code here\n}"
                },
                "tags": ["Linked List"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 2 4\n3\n1 3 4\n3", "expected_output": "1 1 2 3 4 4", "is_hidden": False},
                    {"input_data": "\n0\n\n0", "expected_output": "", "is_hidden": True},
                ]
            },
            {
                "title": "Climbing Stairs",
                "slug": "climbing-stairs",
                "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= n <= 45",
                "examples": [
                    {"input": "n = 2", "output": "2"},
                    {"input": "n = 3", "output": "3"},
                ],
                "starter_code": {
                    "python": "def climbStairs(n):\n    # Write your code here\n    pass",
                    "cpp": "int climbStairs(int n) {\n    // Write your code here\n}",
                    "java": "public int climbStairs(int n) {\n    // Write your code here\n}",
                    "javascript": "function climbStairs(n) {\n    // Write your code here\n}"
                },
                "tags": ["Dynamic Programming"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "2", "expected_output": "2", "is_hidden": False},
                    {"input_data": "3", "expected_output": "3", "is_hidden": False},
                ]
            },
            {
                "title": "Binary Search",
                "slug": "binary-search",
                "description": "Given a sorted array of n integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= nums.length <= 10^4\n-10^4 <= nums[i], target <= 10^4",
                "examples": [
                    {"input": "nums = [1,3,5,6], target = 5", "output": "2"},
                    {"input": "nums = [1,3,5,6], target = 2", "output": "1"},
                ],
                "starter_code": {
                    "python": "def searchInsert(nums, target):\n    # Write your code here\n    pass",
                    "cpp": "int searchInsert(vector<int>& nums, int target) {\n    // Write your code here\n}",
                    "java": "public int searchInsert(int[] nums, int target) {\n    // Write your code here\n}",
                    "javascript": "function searchInsert(nums, target) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Binary Search"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 3 5 6\n5", "expected_output": "2", "is_hidden": False},
                    {"input_data": "1 3 5 6\n2", "expected_output": "1", "is_hidden": False},
                ]
            },
            {
                "title": "Validate Binary Search Tree",
                "slug": "validate-binary-search-tree",
                "description": "Given the root of a binary tree, determine if it is a valid binary search tree (BST).",
                "difficulty": "medium",
                "status": "published",
                "constraints": "The number of nodes in the tree is in the range [1, 10^4].\n-2^31 <= Node.val <= 2^31 - 1",
                "examples": [
                    {"input": "root = [2,1,3]", "output": "true"},
                    {"input": "root = [5,1,4,null,null,3,6]", "output": "false"},
                ],
                "starter_code": {
                    "python": "def isValidBST(root):\n    # Write your code here\n    pass",
                    "cpp": "bool isValidBST(TreeNode* root) {\n    // Write your code here\n}",
                    "java": "public boolean isValidBST(TreeNode root) {\n    // Write your code here\n}",
                    "javascript": "function isValidBST(root) {\n    // Write your code here\n}"
                },
                "tags": ["Tree", "Binary Search"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "2 1 3\n3", "expected_output": "true", "is_hidden": False},
                    {"input_data": "5 1 4 null null 3 6\n7", "expected_output": "false", "is_hidden": True},
                ]
            },
            {
                "title": "Word Break",
                "slug": "word-break",
                "description": "Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= s.length <= 300\n1 <= wordDict.length <= 1000\n1 <= wordDict[i].length <= 20\ns and wordDict[i] consist of only lowercase English letters.",
                "examples": [
                    {"input": "s = 'leetcode', wordDict = ['leet','code']", "output": "true"},
                    {"input": "s = 'applepenapple', wordDict = ['apple','pen']", "output": "true"},
                    {"input": "s = 'catsandog', wordDict = ['cats','dog','sand','and','cat']", "output": "false"},
                ],
                "starter_code": {
                    "python": "def wordBreak(s, wordDict):\n    # Write your code here\n    pass",
                    "cpp": "bool wordBreak(string s, vector<string>& wordDict) {\n    // Write your code here\n}",
                    "java": "public boolean wordBreak(String s, List<String> wordDict) {\n    // Write your code here\n}",
                    "javascript": "function wordBreak(s, wordDict) {\n    // Write your code here\n}"
                },
                "tags": ["Dynamic Programming", "Strings"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "leetcode\n2\nleet code", "expected_output": "true", "is_hidden": False},
                    {"input_data": "catsandog\n5\ncats dog sand and cat", "expected_output": "false", "is_hidden": True},
                ]
            },
        ]

        # Add 25 new problems
        problems_data += [
            {
                "title": "Palindrome Number",
                "slug": "palindrome-number",
                "description": "Given an integer x, return true if x is a palindrome, and false otherwise.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "-2^31 <= x <= 2^31 - 1",
                "examples": [
                    {"input": "x = 121", "output": "true"},
                    {"input": "x = -121", "output": "false"},
                ],
                "starter_code": {
                    "python": "def isPalindrome(x):\n    # Write your code here\n    pass",
                    "cpp": "bool isPalindrome(int x) {\n    // Write your code here\n}",
                    "java": "public boolean isPalindrome(int x) {\n    // Write your code here\n}",
                    "javascript": "function isPalindrome(x) {\n    // Write your code here\n}"
                },
                "tags": ["Math"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "121", "expected_output": "true", "is_hidden": False},
                    {"input_data": "-121", "expected_output": "false", "is_hidden": False},
                ]
            },
            {
                "title": "Remove Duplicates from Sorted Array",
                "slug": "remove-duplicates-from-sorted-array",
                "description": "Given a sorted array nums, remove the duplicates in-place such that each element appears only once and return the new length.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= nums.length <= 3 * 10^4\n-100 <= nums[i] <= 100\nnums is sorted in non-decreasing order.",
                "examples": [
                    {"input": "nums = [1,1,2]", "output": "2, nums = [1,2,_]"},
                    {"input": "nums = [0,0,1,1,1,2,2,3,3,4]", "output": "5, nums = [0,1,2,3,4,_,_,_,_,_]"},
                ],
                "starter_code": {
                    "python": "def removeDuplicates(nums):\n    # Write your code here\n    pass",
                    "cpp": "int removeDuplicates(vector<int>& nums) {\n    // Write your code here\n}",
                    "java": "public int removeDuplicates(int[] nums) {\n    // Write your code here\n}",
                    "javascript": "function removeDuplicates(nums) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 1 2\n3", "expected_output": "2", "is_hidden": False},
                    {"input_data": "0 0 1 1 1 2 2 3 3 4\n10", "expected_output": "5", "is_hidden": False},
                ]
            },
            {
                "title": "Implement strStr()",
                "slug": "implement-strstr",
                "description": "Return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= haystack.length, needle.length <= 10^4",
                "examples": [
                    {"input": "haystack = 'hello', needle = 'll'", "output": "2"},
                    {"input": "haystack = 'aaaaa', needle = 'bba'", "output": "-1"},
                ],
                "starter_code": {
                    "python": "def strStr(haystack, needle):\n    # Write your code here\n    pass",
                    "cpp": "int strStr(string haystack, string needle) {\n    // Write your code here\n}",
                    "java": "public int strStr(String haystack, String needle) {\n    // Write your code here\n}",
                    "javascript": "function strStr(haystack, needle) {\n    // Write your code here\n}"
                },
                "tags": ["Strings"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "hello\nll", "expected_output": "2", "is_hidden": False},
                    {"input_data": "aaaaa\nbba", "expected_output": "-1", "is_hidden": False},
                ]
            },
            {
                "title": "Merge Intervals",
                "slug": "merge-intervals",
                "description": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= starti <= endi <= 10^4",
                "examples": [
                    {"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]"},
                    {"input": "intervals = [[1,4],[4,5]]", "output": "[[1,5]]"},
                ],
                "starter_code": {
                    "python": "def merge(intervals):\n    # Write your code here\n    pass",
                    "cpp": "vector<vector<int>> merge(vector<vector<int>>& intervals) {\n    // Write your code here\n}",
                    "java": "public int[][] merge(int[][] intervals) {\n    // Write your code here\n}",
                    "javascript": "function merge(intervals) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 3\n2 6\n8 10\n15 18\n4", "expected_output": "1 6\n8 10\n15 18", "is_hidden": False},
                    {"input_data": "1 4\n4 5\n2", "expected_output": "1 5", "is_hidden": False},
                ]
            },
            {
                "title": "Longest Substring Without Repeating Characters",
                "slug": "longest-substring-without-repeating-characters",
                "description": "Given a string s, find the length of the longest substring without repeating characters.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "0 <= s.length <= 5 * 10^4",
                "examples": [
                    {"input": "s = 'abcabcbb'", "output": "3"},
                    {"input": "s = 'bbbbb'", "output": "1"},
                ],
                "starter_code": {
                    "python": "def lengthOfLongestSubstring(s):\n    # Write your code here\n    pass",
                    "cpp": "int lengthOfLongestSubstring(string s) {\n    // Write your code here\n}",
                    "java": "public int lengthOfLongestSubstring(String s) {\n    // Write your code here\n}",
                    "javascript": "function lengthOfLongestSubstring(s) {\n    // Write your code here\n}"
                },
                "tags": ["Strings"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "abcabcbb", "expected_output": "3", "is_hidden": False},
                    {"input_data": "bbbbb", "expected_output": "1", "is_hidden": False},
                ]
            },
            {
                "title": "Container With Most Water",
                "slug": "container-with-most-water",
                "description": "Given n non-negative integers a1, a2, ..., an , where each represents a point at coordinate (i, ai). n vertical lines are drawn such that the two endpoints of the line i is at (i, ai) and (i, 0). Find two lines, which together with the x-axis forms a container, such that the container contains the most water.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "n == height.length\n2 <= n <= 10^5\n0 <= height[i] <= 10^4",
                "examples": [
                    {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49"},
                    {"input": "height = [1,1]", "output": "1"},
                ],
                "starter_code": {
                    "python": "def maxArea(height):\n    # Write your code here\n    pass",
                    "cpp": "int maxArea(vector<int>& height) {\n    // Write your code here\n}",
                    "java": "public int maxArea(int[] height) {\n    // Write your code here\n}",
                    "javascript": "function maxArea(height) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Two Pointers"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 8 6 2 5 4 8 3 7\n9", "expected_output": "49", "is_hidden": False},
                    {"input_data": "1 1\n2", "expected_output": "1", "is_hidden": False},
                ]
            },
            {
                "title": "Add Two Numbers",
                "slug": "add-two-numbers",
                "description": "You are given two non-empty linked lists representing two non-negative integers. Add the two numbers and return the sum as a linked list.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "The number of nodes in each linked list is in the range [1, 100].\n0 <= Node.val <= 9\nIt is guaranteed that the list represents a number that does not have leading zeros.",
                "examples": [
                    {"input": "l1 = [2,4,3], l2 = [5,6,4]", "output": "[7,0,8]"},
                    {"input": "l1 = [0], l2 = [0]", "output": "[0]"},
                ],
                "starter_code": {
                    "python": "def addTwoNumbers(l1, l2):\n    # Write your code here\n    pass",
                    "cpp": "ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {\n    // Write your code here\n}",
                    "java": "public ListNode addTwoNumbers(ListNode l1, ListNode l2) {\n    // Write your code here\n}",
                    "javascript": "function addTwoNumbers(l1, l2) {\n    // Write your code here\n}"
                },
                "tags": ["Linked List"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "2 4 3\n3\n5 6 4\n3", "expected_output": "7 0 8", "is_hidden": False},
                    {"input_data": "0\n1\n0\n1", "expected_output": "0", "is_hidden": False},
                ]
            },
            {
                "title": "Valid Palindrome",
                "slug": "valid-palindrome",
                "description": "Given a string s, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= s.length <= 2 * 10^5",
                "examples": [
                    {"input": "s = 'A man, a plan, a canal: Panama'", "output": "true"},
                    {"input": "s = 'race a car'", "output": "false"},
                ],
                "starter_code": {
                    "python": "def isPalindrome(s):\n    # Write your code here\n    pass",
                    "cpp": "bool isPalindrome(string s) {\n    // Write your code here\n}",
                    "java": "public boolean isPalindrome(String s) {\n    // Write your code here\n}",
                    "javascript": "function isPalindrome(s) {\n    // Write your code here\n}"
                },
                "tags": ["Strings", "Two Pointers"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "A man, a plan, a canal: Panama", "expected_output": "true", "is_hidden": False},
                    {"input_data": "race a car", "expected_output": "false", "is_hidden": False},
                ]
            },
            {
                "title": "Search Insert Position",
                "slug": "search-insert-position",
                "description": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= nums.length <= 10^4\n-10^4 <= nums[i] <= 10^4\nnums contains distinct values sorted in ascending order.",
                "examples": [
                    {"input": "nums = [1,3,5,6], target = 5", "output": "2"},
                    {"input": "nums = [1,3,5,6], target = 2", "output": "1"},
                ],
                "starter_code": {
                    "python": "def searchInsert(nums, target):\n    # Write your code here\n    pass",
                    "cpp": "int searchInsert(vector<int>& nums, int target) {\n    // Write your code here\n}",
                    "java": "public int searchInsert(int[] nums, int target) {\n    // Write your code here\n}",
                    "javascript": "function searchInsert(nums, target) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Binary Search"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 3 5 6\n4\n5", "expected_output": "2", "is_hidden": False},
                    {"input_data": "1 3 5 6\n4\n2", "expected_output": "1", "is_hidden": False},
                ]
            },
            {
                "title": "Plus One",
                "slug": "plus-one",
                "description": "Given a non-empty array of decimal digits representing a non-negative integer, increment one to the integer.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= digits.length <= 100\n0 <= digits[i] <= 9",
                "examples": [
                    {"input": "digits = [1,2,3]", "output": "[1,2,4]"},
                    {"input": "digits = [4,3,2,1]", "output": "[4,3,2,2]"},
                ],
                "starter_code": {
                    "python": "def plusOne(digits):\n    # Write your code here\n    pass",
                    "cpp": "vector<int> plusOne(vector<int>& digits) {\n    // Write your code here\n}",
                    "java": "public int[] plusOne(int[] digits) {\n    // Write your code here\n}",
                    "javascript": "function plusOne(digits) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 2 3\n3", "expected_output": "1 2 4", "is_hidden": False},
                    {"input_data": "4 3 2 1\n4", "expected_output": "4 3 2 2", "is_hidden": False},
                ]
            },
            {
                "title": "Sqrt(x)",
                "slug": "sqrtx",
                "description": "Given a non-negative integer x, compute and return the square root of x.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "0 <= x <= 2^31 - 1",
                "examples": [
                    {"input": "x = 4", "output": "2"},
                    {"input": "x = 8", "output": "2"},
                ],
                "starter_code": {
                    "python": "def mySqrt(x):\n    # Write your code here\n    pass",
                    "cpp": "int mySqrt(int x) {\n    // Write your code here\n}",
                    "java": "public int mySqrt(int x) {\n    // Write your code here\n}",
                    "javascript": "function mySqrt(x) {\n    // Write your code here\n}"
                },
                "tags": ["Math", "Binary Search"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "4", "expected_output": "2", "is_hidden": False},
                    {"input_data": "8", "expected_output": "2", "is_hidden": False},
                ]
            },
            {
                "title": "Roman to Integer",
                "slug": "roman-to-integer",
                "description": "Given a roman numeral, convert it to an integer.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= s.length <= 15\ns contains only the characters ('I', 'V', 'X', 'L', 'C', 'D', 'M')",
                "examples": [
                    {"input": "s = 'III'", "output": "3"},
                    {"input": "s = 'IV'", "output": "4"},
                ],
                "starter_code": {
                    "python": "def romanToInt(s):\n    # Write your code here\n    pass",
                    "cpp": "int romanToInt(string s) {\n    // Write your code here\n}",
                    "java": "public int romanToInt(String s) {\n    // Write your code here\n}",
                    "javascript": "function romanToInt(s) {\n    // Write your code here\n}"
                },
                "tags": ["Strings"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "III", "expected_output": "3", "is_hidden": False},
                    {"input_data": "IV", "expected_output": "4", "is_hidden": False},
                ]
            },
            {
                "title": "Valid Anagram",
                "slug": "valid-anagram",
                "description": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= s.length, t.length <= 5 * 10^4",
                "examples": [
                    {"input": "s = 'anagram', t = 'nagaram'", "output": "true"},
                    {"input": "s = 'rat', t = 'car'", "output": "false"},
                ],
                "starter_code": {
                    "python": "def isAnagram(s, t):\n    # Write your code here\n    pass",
                    "cpp": "bool isAnagram(string s, string t) {\n    // Write your code here\n}",
                    "java": "public boolean isAnagram(String s, String t) {\n    // Write your code here\n}",
                    "javascript": "function isAnagram(s, t) {\n    // Write your code here\n}"
                },
                "tags": ["Strings", "Hash Table"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "anagram\nnagaram", "expected_output": "true", "is_hidden": False},
                    {"input_data": "rat\ncar", "expected_output": "false", "is_hidden": False},
                ]
            },
            {
                "title": "Intersection of Two Arrays II",
                "slug": "intersection-of-two-arrays-ii",
                "description": "Given two integer arrays nums1 and nums2, return an array of their intersection.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= nums1.length, nums2.length <= 1000\n0 <= nums1[i], nums2[i] <= 1000",
                "examples": [
                    {"input": "nums1 = [1,2,2,1], nums2 = [2,2]", "output": "[2,2]"},
                    {"input": "nums1 = [4,9,5], nums2 = [9,4,9,8,4]", "output": "[4,9]"},
                ],
                "starter_code": {
                    "python": "def intersect(nums1, nums2):\n    # Write your code here\n    pass",
                    "cpp": "vector<int> intersect(vector<int>& nums1, vector<int>& nums2) {\n    // Write your code here\n}",
                    "java": "public int[] intersect(int[] nums1, int[] nums2) {\n    // Write your code here\n}",
                    "javascript": "function intersect(nums1, nums2) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Hash Table"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "1 2 2 1\n4\n2 2\n2", "expected_output": "2 2", "is_hidden": False},
                    {"input_data": "4 9 5\n3\n9 4 9 8 4\n5", "expected_output": "4 9", "is_hidden": False},
                ]
            },
            {
                "title": "Majority Element",
                "slug": "majority-element",
                "description": "Given an array nums of size n, return the majority element.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "n == nums.length\n1 <= n <= 5 * 10^4\n-10^9 <= nums[i] <= 10^9",
                "examples": [
                    {"input": "nums = [3,2,3]", "output": "3"},
                    {"input": "nums = [2,2,1,1,1,2,2]", "output": "2"},
                ],
                "starter_code": {
                    "python": "def majorityElement(nums):\n    # Write your code here\n    pass",
                    "cpp": "int majorityElement(vector<int>& nums) {\n    // Write your code here\n}",
                    "java": "public int majorityElement(int[] nums) {\n    // Write your code here\n}",
                    "javascript": "function majorityElement(nums) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Hash Table"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "3 2 3\n3", "expected_output": "3", "is_hidden": False},
                    {"input_data": "2 2 1 1 1 2 2\n7", "expected_output": "2", "is_hidden": False},
                ]
            },
            {
                "title": "Move Zeroes",
                "slug": "move-zeroes",
                "description": "Given an integer array nums, move all 0's to the end of it while maintaining the relative order of the non-zero elements.",
                "difficulty": "easy",
                "status": "published",
                "constraints": "1 <= nums.length <= 10^4\n-2^31 <= nums[i] <= 2^31 - 1",
                "examples": [
                    {"input": "nums = [0,1,0,3,12]", "output": "[1,3,12,0,0]"},
                    {"input": "nums = [0]", "output": "[0]"},
                ],
                "starter_code": {
                    "python": "def moveZeroes(nums):\n    # Write your code here\n    pass",
                    "cpp": "void moveZeroes(vector<int>& nums) {\n    // Write your code here\n}",
                    "java": "public void moveZeroes(int[] nums) {\n    // Write your code here\n}",
                    "javascript": "function moveZeroes(nums) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays", "Two Pointers"],
                "coin_reward": 10,
                "xp_reward": 50,
                "test_cases": [
                    {"input_data": "0 1 0 3 12\n5", "expected_output": "1 3 12 0 0", "is_hidden": False},
                    {"input_data": "0\n1", "expected_output": "0", "is_hidden": False},
                ]
            },
            {
                "title": "Minimum Path Sum",
                "slug": "minimum-path-sum",
                "description": "Given a m x n grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "m == grid.length\nn == grid[i].length\n1 <= m, n <= 200\n0 <= grid[i][j] <= 100",
                "examples": [
                    {"input": "grid = [[1,3,1],[1,5,1],[4,2,1]]", "output": "7"},
                    {"input": "grid = [[1,2,3],[4,5,6]]", "output": "12"},
                ],
                "starter_code": {
                    "python": "def minPathSum(grid):\n    # Write your code here\n    pass",
                    "cpp": "int minPathSum(vector<vector<int>>& grid) {\n    // Write your code here\n}",
                    "java": "public int minPathSum(int[][] grid) {\n    // Write your code here\n}",
                    "javascript": "function minPathSum(grid) {\n    // Write your code here\n}"
                },
                "tags": ["Dynamic Programming"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 3 1\n1 5 1\n4 2 1\n3 3", "expected_output": "7", "is_hidden": False},
                    {"input_data": "1 2 3\n4 5 6\n2 3", "expected_output": "12", "is_hidden": False},
                ]
            },
            {
                "title": "Unique Paths",
                "slug": "unique-paths",
                "description": "A robot is located at the top-left corner of a m x n grid. The robot can only move either down or right at any point in time. Return the number of possible unique paths that the robot can take to reach the bottom-right corner.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= m, n <= 100",
                "examples": [
                    {"input": "m = 3, n = 7", "output": "28"},
                    {"input": "m = 3, n = 2", "output": "3"},
                ],
                "starter_code": {
                    "python": "def uniquePaths(m, n):\n    # Write your code here\n    pass",
                    "cpp": "int uniquePaths(int m, int n) {\n    // Write your code here\n}",
                    "java": "public int uniquePaths(int m, int n) {\n    // Write your code here\n}",
                    "javascript": "function uniquePaths(m, n) {\n    // Write your code here\n}"
                },
                "tags": ["Dynamic Programming"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "3 7", "expected_output": "28", "is_hidden": False},
                    {"input_data": "3 2", "expected_output": "3", "is_hidden": False},
                ]
            },
            {
                "title": "Set Matrix Zeroes",
                "slug": "set-matrix-zeroes",
                "description": "Given an m x n integer matrix, if an element is 0, set its entire row and column to 0.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "m == matrix.length\nn == matrix[0].length\n1 <= m, n <= 200\n-2^31 <= matrix[i][j] <= 2^31 - 1",
                "examples": [
                    {"input": "matrix = [[1,1,1],[1,0,1],[1,1,1]]", "output": "[[1,0,1],[0,0,0],[1,0,1]]"},
                    {"input": "matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]", "output": "[[0,0,0,0],[0,4,5,0],[0,3,1,0]]"},
                ],
                "starter_code": {
                    "python": "def setZeroes(matrix):\n    # Write your code here\n    pass",
                    "cpp": "void setZeroes(vector<vector<int>>& matrix) {\n    // Write your code here\n}",
                    "java": "public void setZeroes(int[][] matrix) {\n    // Write your code here\n}",
                    "javascript": "function setZeroes(matrix) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 1 1\n1 0 1\n1 1 1\n3 3", "expected_output": "1 0 1\n0 0 0\n1 0 1", "is_hidden": False},
                    {"input_data": "0 1 2 0\n3 4 5 2\n1 3 1 5\n3 4", "expected_output": "0 0 0 0\n0 4 5 0\n0 3 1 0", "is_hidden": False},
                ]
            },
            {
                "title": "Spiral Matrix",
                "slug": "spiral-matrix",
                "description": "Given an m x n matrix, return all elements of the matrix in spiral order.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "m == matrix.length\nn == matrix[0].length\n1 <= m, n <= 10",
                "examples": [
                    {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[1,2,3,6,9,8,7,4,5]"},
                    {"input": "matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]", "output": "[1,2,3,4,8,12,11,10,9,5,6,7]"},
                ],
                "starter_code": {
                    "python": "def spiralOrder(matrix):\n    # Write your code here\n    pass",
                    "cpp": "vector<int> spiralOrder(vector<vector<int>>& matrix) {\n    // Write your code here\n}",
                    "java": "public List<Integer> spiralOrder(int[][] matrix) {\n    // Write your code here\n}",
                    "javascript": "function spiralOrder(matrix) {\n    // Write your code here\n}"
                },
                "tags": ["Arrays"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 2 3\n4 5 6\n7 8 9\n3 3", "expected_output": "1 2 3 6 9 8 7 4 5", "is_hidden": False},
                    {"input_data": "1 2 3 4\n5 6 7 8\n9 10 11 12\n3 4", "expected_output": "1 2 3 4 8 12 11 10 9 5 6 7", "is_hidden": False},
                ]
            },
            {
                "title": "Number of Islands",
                "slug": "number-of-islands",
                "description": "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "m == grid.length\nn == grid[i].length\n1 <= m, n <= 300",
                "examples": [
                    {"input": "grid = [[1,1,1,1,0],[1,1,0,1,0],[1,1,0,0,0],[0,0,0,0,0]]", "output": "1"},
                    {"input": "grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,1,0,0],[0,0,0,1,1]]", "output": "3"},
                ],
                "starter_code": {
                    "python": "def numIslands(grid):\n    # Write your code here\n    pass",
                    "cpp": "int numIslands(vector<vector<char>>& grid) {\n    // Write your code here\n}",
                    "java": "public int numIslands(char[][] grid) {\n    // Write your code here\n}",
                    "javascript": "function numIslands(grid) {\n    // Write your code here\n}"
                },
                "tags": ["DFS", "BFS"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0\n4 5", "expected_output": "1", "is_hidden": False},
                    {"input_data": "1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1\n4 5", "expected_output": "3", "is_hidden": False},
                ]
            },
            {
                "title": "Word Search",
                "slug": "word-search",
                "description": "Given an m x n grid of characters board and a string word, return true if word exists in the grid.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "m == board.length\nn == board[i].length\n1 <= m, n <= 6\n1 <= word.length <= 15",
                "examples": [
                    {"input": "board = [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']], word = 'ABCCED'", "output": "true"},
                    {"input": "board = [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']], word = 'SEE'", "output": "true"},
                ],
                "starter_code": {
                    "python": "def exist(board, word):\n    # Write your code here\n    pass",
                    "cpp": "bool exist(vector<vector<char>>& board, string word) {\n    // Write your code here\n}",
                    "java": "public boolean exist(char[][] board, String word) {\n    // Write your code here\n}",
                    "javascript": "function exist(board, word) {\n    // Write your code here\n}"
                },
                "tags": ["DFS", "Backtracking"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "A B C E\nS F C S\nA D E E\n3 4\nABCCED", "expected_output": "true", "is_hidden": False},
                    {"input_data": "A B C E\nS F C S\nA D E E\n3 4\nSEE", "expected_output": "true", "is_hidden": False},
                ]
            },
            {
                "title": "Combination Sum",
                "slug": "combination-sum",
                "description": "Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= candidates.length <= 30\n1 <= candidates[i] <= 200\nAll elements of candidates are distinct.\n1 <= target <= 500",
                "examples": [
                    {"input": "candidates = [2,3,6,7], target = 7", "output": "[[2,2,3],[7]]"},
                    {"input": "candidates = [2,3,5], target = 8", "output": "[[2,2,2,2],[2,3,3],[3,5]]"},
                ],
                "starter_code": {
                    "python": "def combinationSum(candidates, target):\n    # Write your code here\n    pass",
                    "cpp": "vector<vector<int>> combinationSum(vector<int>& candidates, int target) {\n    // Write your code here\n}",
                    "java": "public List<List<Integer>> combinationSum(int[] candidates, int target) {\n    // Write your code here\n}",
                    "javascript": "function combinationSum(candidates, target) {\n    // Write your code here\n}"
                },
                "tags": ["Backtracking"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "2 3 6 7\n4\n7", "expected_output": "2 2 3\n7", "is_hidden": False},
                    {"input_data": "2 3 5\n3\n8", "expected_output": "2 2 2 2\n2 3 3\n3 5", "is_hidden": False},
                ]
            },
            {
                "title": "Permutations",
                "slug": "permutations",
                "description": "Given an array nums of distinct integers, return all the possible permutations.",
                "difficulty": "medium",
                "status": "published",
                "constraints": "1 <= nums.length <= 6\n-10 <= nums[i] <= 10",
                "examples": [
                    {"input": "nums = [1,2,3]", "output": "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]"},
                    {"input": "nums = [0,1]", "output": "[[0,1],[1,0]]"},
                ],
                "starter_code": {
                    "python": "def permute(nums):\n    # Write your code here\n    pass",
                    "cpp": "vector<vector<int>> permute(vector<int>& nums) {\n    // Write your code here\n}",
                    "java": "public List<List<Integer>> permute(int[] nums) {\n    // Write your code here\n}",
                    "javascript": "function permute(nums) {\n    // Write your code here\n}"
                },
                "tags": ["Backtracking"],
                "coin_reward": 20,
                "xp_reward": 100,
                "test_cases": [
                    {"input_data": "1 2 3\n3", "expected_output": "1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1", "is_hidden": False},
                    {"input_data": "0 1\n2", "expected_output": "0 1\n1 0", "is_hidden": False},
                ]
            },
        ]

        for pdata in problems_data:
            problem, created = Problem.objects.get_or_create(
                slug=pdata["slug"],
                defaults={
                    "title": pdata["title"],
                    "description": pdata["description"],
                    "difficulty": pdata["difficulty"],
                    "status": pdata["status"],
                    "constraints": pdata["constraints"],
                    "examples": pdata["examples"],
                    "starter_code": pdata["starter_code"],
                    "created_by": admin_user,
                    "coin_reward": pdata["coin_reward"],
                    "xp_reward": pdata["xp_reward"],
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                }
            )
            # Add tags
            for tag_name in pdata["tags"]:
                problem.tags.add(tag_objs[tag_name])
            # Add test cases
            for i, tdata in enumerate(pdata["test_cases"]):
                TestCase.objects.get_or_create(
                    problem=problem,
                    order=i,
                    defaults={
                        "input_data": tdata["input_data"],
                        "expected_output": tdata["expected_output"],
                        "is_hidden": tdata["is_hidden"],
                        "time_limit": 1.0,
                        "memory_limit": 128,
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"Added problem: {problem.title}")) 