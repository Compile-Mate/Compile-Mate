from problems.models import Problem, Tag, TestCase
from users.models import User
from django.utils import timezone

# Create or get tags
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
]
tag_objs = {}
for name, desc, color in TAGS:
    tag, _ = Tag.objects.get_or_create(name=name, defaults={"description": desc, "color": color})
    tag_objs[name] = tag

# Get an admin user (or first user)
admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

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
            {"input_data": "7 1 5 3 6 4", "expected_output": "5", "is_hidden": False},
            {"input_data": "7 6 4 3 1", "expected_output": "0", "is_hidden": False},
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
    print(f"Added problem: {problem.title}") 