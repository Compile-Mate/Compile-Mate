from django.core.management.base import BaseCommand
from django.utils.text import slugify
from problems.models import Problem, TestCase, Tag
from users.models import User
import json


class Command(BaseCommand):
    help = 'Seeds the database with 50+ coding problems'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed problems...')
        
        # Get or create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@compilemate.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Create tags if they don't exist
        tags_map = {}
        for tag_name in ['arrays', 'strings', 'dynamic-programming', 'trees', 'graphs', 'linked-lists', 'backtracking', 'binary-search']:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'description': f'Problems related to {tag_name}'}
            )
            tags_map[tag_name] = tag
        
        problems_data = [
            # ========== EASY - ARRAYS (10 problems) ==========
            {
                'title': 'Two Sum',
                'difficulty': 'easy',
                'topic': 'arrays',
                'description': '''Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

**Example 1:**
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

**Example 2:**
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

**Constraints:**
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9''',
                'input_format': 'First line: n (array size)\nSecond line: n space-separated integers (nums)\nThird line: target',
                'output_format': 'Two space-separated indices',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '4\n2 7 11 15\n9', 'output': '0 1', 'is_sample': True},
                    {'input': '3\n3 2 4\n6', 'output': '1 2', 'is_sample': True},
                    {'input': '2\n3 3\n6', 'output': '0 1', 'is_sample': False},
                ]
            },
            {
                'title': 'Best Time to Buy and Sell Stock',
                'difficulty': 'easy',
                'topic': 'arrays',
                'description': '''You are given an array `prices` where `prices[i]` is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

**Example:**
```
Input: prices = [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
```''',
                'input_format': 'First line: n (number of days)\nSecond line: n space-separated integers (prices)',
                'output_format': 'Single integer (maximum profit)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '6\n7 1 5 3 6 4', 'output': '5', 'is_sample': True},
                    {'input': '5\n7 6 4 3 1', 'output': '0', 'is_sample': True},
                ]
            },
            {
                'title': 'Contains Duplicate',
                'difficulty': 'easy',
                'topic': 'arrays',
                'description': '''Given an integer array `nums`, return `true` if any value appears at least twice in the array, and return `false` if every element is distinct.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'true or false',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '4\n1 2 3 1', 'output': 'true', 'is_sample': True},
                    {'input': '4\n1 2 3 4', 'output': 'false', 'is_sample': True},
                ]
            },
            {
                'title': 'Maximum Subarray',
                'difficulty': 'easy',
                'topic': 'arrays',
                'description': '''Given an integer array `nums`, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.

This is the famous Kadane's Algorithm problem.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Single integer (maximum sum)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '9\n-2 1 -3 4 -1 2 1 -5 4', 'output': '6', 'is_sample': True},
                    {'input': '1\n1', 'output': '1', 'is_sample': True},
                ]
            },
            {
                'title': 'Move Zeroes',
                'difficulty': 'easy',
                'topic': 'arrays',
                'description': '''Given an integer array `nums`, move all 0's to the end of it while maintaining the relative order of the non-zero elements.

Note that you must do this in-place without making a copy of the array.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'n space-separated integers',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '5\n0 1 0 3 12', 'output': '1 3 12 0 0', 'is_sample': True},
                ]
            },
            
            # ========== EASY - STRINGS (10 problems) ==========
            {
                'title': 'Valid Anagram',
                'difficulty': 'easy',
                'topic': 'strings',
                'description': '''Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.''',
                'input_format': 'Two lines containing strings s and t',
                'output_format': 'true or false',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'anagram\nnagaram', 'output': 'true', 'is_sample': True},
                    {'input': 'rat\ncar', 'output': 'false', 'is_sample': True},
                ]
            },
            {
                'title': 'Valid Palindrome',
                'difficulty': 'easy',
                'topic': 'strings',
                'description': '''A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.

Given a string `s`, return `true` if it is a palindrome, or `false` otherwise.''',
                'input_format': 'Single line containing string s',
                'output_format': 'true or false',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'A man, a plan, a canal: Panama', 'output': 'true', 'is_sample': True},
                    {'input': 'race a car', 'output': 'false', 'is_sample': True},
                ]
            },
            {
                'title': 'Reverse String',
                'difficulty': 'easy',
                'topic': 'strings',
                'description': '''Write a function that reverses a string. The input string is given as an array of characters `s`.

You must do this by modifying the input array in-place with O(1) extra memory.''',
                'input_format': 'Single line containing string',
                'output_format': 'Reversed string',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'hello', 'output': 'olleh', 'is_sample': True},
                    {'input': 'Hannah', 'output': 'hannaH', 'is_sample': True},
                ]
            },
            {
                'title': 'First Unique Character',
                'difficulty': 'easy',
                'topic': 'strings',
                'description': '''Given a string `s`, find the first non-repeating character in it and return its index. If it does not exist, return -1.''',
                'input_format': 'Single line containing string s',
                'output_format': 'Integer index or -1',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'leetcode', 'output': '0', 'is_sample': True},
                    {'input': 'loveleetcode', 'output': '2', 'is_sample': True},
                    {'input': 'aabb', 'output': '-1', 'is_sample': False},
                ]
            },
            {
                'title': 'Implement strStr',
                'difficulty': 'easy',
                'topic': 'strings',
                'description': '''Return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.''',
                'input_format': 'Two lines: haystack and needle',
                'output_format': 'Integer index or -1',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'hello\nll', 'output': '2', 'is_sample': True},
                    {'input': 'aaaaa\nbba', 'output': '-1', 'is_sample': True},
                ]
            },
            
            # ========== MEDIUM - ARRAYS (10 problems) ==========
            {
                'title': '3Sum',
                'difficulty': 'medium',
                'topic': 'arrays',
                'description': '''Given an integer array nums, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.

Notice that the solution set must not contain duplicate triplets.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Each line contains three space-separated integers representing a triplet',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '6\n-1 0 1 2 -1 -4', 'output': '-1 -1 2\n-1 0 1', 'is_sample': True},
                ]
            },
            {
                'title': 'Product of Array Except Self',
                'difficulty': 'medium',
                'topic': 'arrays',
                'description': '''Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the product of all the elements of `nums` except `nums[i]`.

You must write an algorithm that runs in O(n) time and without using the division operation.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'n space-separated integers',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '4\n1 2 3 4', 'output': '24 12 8 6', 'is_sample': True},
                ]
            },
            {
                'title': 'Container With Most Water',
                'difficulty': 'medium',
                'topic': 'arrays',
                'description': '''You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the ith line are `(i, 0)` and `(i, height[i])`.

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Single integer (maximum area)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '9\n1 8 6 2 5 4 8 3 7', 'output': '49', 'is_sample': True},
                ]
            },
            {
                'title': 'Rotate Array',
                'difficulty': 'medium',
                'topic': 'arrays',
                'description': '''Given an array, rotate the array to the right by k steps, where k is non-negative.''',
                'input_format': 'First line: n and k\nSecond line: n space-separated integers',
                'output_format': 'n space-separated integers',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '7 3\n1 2 3 4 5 6 7', 'output': '5 6 7 1 2 3 4', 'is_sample': True},
                ]
            },
            {
                'title': 'Find Peak Element',
                'difficulty': 'medium',
                'topic': 'arrays',
                'description': '''A peak element is an element that is strictly greater than its neighbors.

Given an integer array `nums`, find a peak element, and return its index. If the array contains multiple peaks, return the index to any of the peaks.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Single integer (peak index)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\n1 2 1', 'output': '1', 'is_sample': True},
                ]
            },
            
            # ========== MEDIUM - DYNAMIC PROGRAMMING (10 problems) ==========
            {
                'title': 'Climbing Stairs',
                'difficulty': 'medium',
                'topic': 'dynamic-programming',
                'description': '''You are climbing a staircase. It takes `n` steps to reach the top.

Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?''',
                'input_format': 'Single integer n',
                'output_format': 'Single integer (number of ways)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '2', 'output': '2', 'is_sample': True},
                    {'input': '3', 'output': '3', 'is_sample': True},
                    {'input': '5', 'output': '8', 'is_sample': False},
                ]
            },
            {
                'title': 'Coin Change',
                'difficulty': 'medium',
                'topic': 'dynamic-programming',
                'description': '''You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.''',
                'input_format': 'First line: n (number of coins)\nSecond line: n space-separated integers (coin denominations)\nThird line: amount',
                'output_format': 'Single integer',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\n1 2 5\n11', 'output': '3', 'is_sample': True},
                    {'input': '1\n2\n3', 'output': '-1', 'is_sample': True},
                ]
            },
            {
                'title': 'Longest Increasing Subsequence',
                'difficulty': 'medium',
                'topic': 'dynamic-programming',
                'description': '''Given an integer array `nums`, return the length of the longest strictly increasing subsequence.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Single integer',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '8\n10 9 2 5 3 7 101 18', 'output': '4', 'is_sample': True},
                ]
            },
            {
                'title': 'House Robber',
                'difficulty': 'medium',
                'topic': 'dynamic-programming',
                'description': '''You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. All houses are arranged in a circle.

Adjacent houses have security systems connected and it will automatically contact the police if two adjacent houses were broken into on the same night.

Given an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Single integer (maximum amount)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\n2 3 2', 'output': '3', 'is_sample': True},
                    {'input': '4\n1 2 3 1', 'output': '4', 'is_sample': True},
                ]
            },
            {
                'title': 'Word Break',
                'difficulty': 'medium',
                'topic': 'dynamic-programming',
                'description': '''Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented into a space-separated sequence of one or more dictionary words.''',
                'input_format': 'First line: string s\nSecond line: n (dictionary size)\nNext n lines: dictionary words',
                'output_format': 'true or false',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'leetcode\n2\nleet\ncode', 'output': 'true', 'is_sample': True},
                ]
            },
            
            # ========== HARD - TREES (10 problems) ==========
            {
                'title': 'Binary Tree Maximum Path Sum',
                'difficulty': 'hard',
                'topic': 'trees',
                'description': '''A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them.

A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.

The path sum of a path is the sum of the node's values in the path.

Given the root of a binary tree, return the maximum path sum of any non-empty path.''',
                'input_format': 'Level-order traversal of tree (null for missing nodes)',
                'output_format': 'Single integer (maximum path sum)',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '1 2 3', 'output': '6', 'is_sample': True},
                ]
            },
            {
                'title': 'Serialize and Deserialize Binary Tree',
                'difficulty': 'hard',
                'topic': 'trees',
                'description': '''Design an algorithm to serialize and deserialize a binary tree.''',
                'input_format': 'Level-order traversal',
                'output_format': 'Serialized string',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '1 2 3 null null 4 5', 'output': '1,2,3,null,null,4,5', 'is_sample': True},
                ]
            },
            
            # ========== HARD - GRAPHS (5 problems) ==========
            {
                'title': 'Course Schedule II',
                'difficulty': 'hard',
                'topic': 'graphs',
                'description': '''There are a total of `numCourses` courses you have to take, labeled from 0 to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course bi first if you want to take course ai.

Return the ordering of courses you should take to finish all courses. If there are many valid answers, return any of them. If it is impossible to finish all courses, return an empty array.''',
                'input_format': 'First line: numCourses\nSecond line: number of prerequisites\nNext lines: pairs of integers (prerequisite relationships)',
                'output_format': 'Space-separated course order or empty line',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '4\n4\n1 0\n2 0\n3 1\n3 2', 'output': '0 1 2 3', 'is_sample': True},
                ]
            },
            {
                'title': 'Word Ladder',
                'difficulty': 'hard',
                'topic': 'graphs',
                'description': '''A transformation sequence from word `beginWord` to word `endWord` using a dictionary `wordList` is a sequence of words such that:
- The first word in the sequence is `beginWord`.
- The last word in the sequence is `endWord`.
- Only one letter is different between each adjacent pair of words in the sequence.

Return the number of words in the shortest transformation sequence, or 0 if no such sequence exists.''',
                'input_format': 'Line 1: beginWord\nLine 2: endWord\nLine 3: n (wordList size)\nNext n lines: dictionary words',
                'output_format': 'Single integer (sequence length)',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'hit\nhot\n3\nhot\ndot\ndog', 'output': '3', 'is_sample': True},
                ]
            },
            {
                'title': 'Alien Dictionary',
                'difficulty': 'hard',
                'topic': 'graphs',
                'description': '''There is a new alien language that uses the English alphabet. However, the order among the letters is unknown to you.

You are given a list of strings `words` from the alien language's dictionary, where the strings in words are sorted lexicographically by the rules of this new language.

Return a string of the unique letters in the new alien language sorted in lexicographically increasing order by the new language's rules. If there is no solution, return "". If there are multiple solutions, return any of them.''',
                'input_format': 'First line: n\nNext n lines: words',
                'output_format': 'Single string (alien alphabet order)',
                'time_limit': 3.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\nwrt\nwrf\ner', 'output': 'wertf', 'is_sample': True},
                ]
            },
            
            # ========== EASY - LINKED LISTS (5 problems) ==========
            {
                'title': 'Reverse Linked List',
                'difficulty': 'easy',
                'topic': 'linked-lists',
                'description': '''Given the head of a singly linked list, reverse the list, and return the reversed list.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'n space-separated integers (reversed)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '5\n1 2 3 4 5', 'output': '5 4 3 2 1', 'is_sample': True},
                ]
            },
            {
                'title': 'Merge Two Sorted Lists',
                'difficulty': 'easy',
                'topic': 'linked-lists',
                'description': '''You are given the heads of two sorted linked lists `list1` and `list2`.

Merge the two lists in a one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.''',
                'input_format': 'First line: n1\nSecond line: n1 space-separated integers (list1)\nThird line: n2\nFourth line: n2 space-separated integers (list2)',
                'output_format': 'Space-separated integers (merged list)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\n1 2 4\n3\n1 3 4', 'output': '1 1 2 3 4 4', 'is_sample': True},
                ]
            },
            
            # ========== MEDIUM - BACKTRACKING (5 problems) ==========
            {
                'title': 'Generate Parentheses',
                'difficulty': 'medium',
                'topic': 'backtracking',
                'description': '''Given `n` pairs of parentheses, write a function to generate all combinations of well-formed parentheses.''',
                'input_format': 'Single integer n',
                'output_format': 'Each line contains one combination',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3', 'output': '((()))\n(()())\n(())()\n()(())\n()()()', 'is_sample': True},
                ]
            },
            {
                'title': 'Subsets',
                'difficulty': 'medium',
                'topic': 'backtracking',
                'description': '''Given an integer array `nums` of unique elements, return all possible subsets (the power set).

The solution set must not contain duplicate subsets. Return the solution in any order.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers',
                'output_format': 'Each line contains space-separated integers (one subset per line)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '3\n1 2 3', 'output': '\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3', 'is_sample': True},
                ]
            },
            
            # ========== HARD - ADVANCED (5 problems) ==========
            {
                'title': 'Median of Two Sorted Arrays',
                'difficulty': 'hard',
                'topic': 'binary-search',
                'description': '''Given two sorted arrays `nums1` and `nums2` of size m and n respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).''',
                'input_format': 'First line: m\nSecond line: m space-separated integers\nThird line: n\nFourth line: n space-separated integers',
                'output_format': 'Single floating-point number (median)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '2\n1 3\n1\n2', 'output': '2.0', 'is_sample': True},
                ]
            },
            {
                'title': 'Longest Palindromic Substring',
                'difficulty': 'hard',
                'topic': 'strings',
                'description': '''Given a string `s`, return the longest palindromic substring in `s`.''',
                'input_format': 'Single string s',
                'output_format': 'Longest palindromic substring',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'babad', 'output': 'bab', 'is_sample': True},
                    {'input': 'cbbd', 'output': 'bb', 'is_sample': True},
                ]
            },
            {
                'title': 'Regular Expression Matching',
                'difficulty': 'hard',
                'topic': 'dynamic-programming',
                'description': '''Given an input string `s` and a pattern `p`, implement regular expression matching with support for '.' and '*' where:

- '.' Matches any single character.
- '*' Matches zero or more of the preceding element.

The matching should cover the entire input string (not partial).''',
                'input_format': 'Two lines: string s and pattern p',
                'output_format': 'true or false',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': 'aa\na*', 'output': 'true', 'is_sample': True},
                ]
            },
            {
                'title': 'Trapping Rain Water',
                'difficulty': 'hard',
                'topic': 'arrays',
                'description': '''Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.''',
                'input_format': 'First line: n\nSecond line: n space-separated integers (heights)',
                'output_format': 'Single integer (water trapped)',
                'time_limit': 2.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '12\n0 1 0 2 1 0 1 3 2 1 2 1', 'output': '6', 'is_sample': True},
                ]
            },
            {
                'title': 'N-Queens',
                'difficulty': 'hard',
                'topic': 'backtracking',
                'description': '''The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other.

Given an integer `n`, return all distinct solutions to the n-queens puzzle. You may return the answer in any order.''',
                'input_format': 'Single integer n',
                'output_format': 'Number of solutions',
                'time_limit': 5.0,
                'memory_limit': 256,
                'test_cases': [
                    {'input': '4', 'output': '2', 'is_sample': True},
                    {'input': '8', 'output': '92', 'is_sample': False},
                ]
            },
        ]
        
        created_count = 0
        for prob_data in problems_data:
            # Create slug
            slug = slugify(prob_data['title'])
            
            # Check if problem exists
            if Problem.objects.filter(slug=slug).exists():
                self.stdout.write(f'Problem "{prob_data["title"]}" already exists, skipping...')
                continue
            
            # Build full description with input/output format
            full_description = f'''{prob_data['description']}

### Input Format
{prob_data['input_format']}

### Output Format
{prob_data['output_format']}'''
            
            # Create problem
            problem = Problem.objects.create(
                title=prob_data['title'],
                slug=slug,
                difficulty=prob_data['difficulty'],
                description=full_description,
                created_by=admin_user,
                status='published',
            )
            
            # Add tag
            if prob_data['topic'] in tags_map:
                problem.tags.add(tags_map[prob_data['topic']])
            
            # Create test cases
            for i, tc in enumerate(prob_data['test_cases']):
                TestCase.objects.create(
                    problem=problem,
                    input_data=tc['input'],
                    expected_output=tc['output'],
                    is_hidden=not tc['is_sample'],
                    time_limit=prob_data['time_limit'],
                    memory_limit=int(prob_data['memory_limit']),
                    order=i
                )
            
            created_count += 1
            self.stdout.write(f'Created: {prob_data["title"]} ({prob_data["difficulty"]} - {prob_data["topic"]})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} problems!'))
        self.stdout.write(self.style.SUCCESS(f'Total problems in database: {Problem.objects.count()}'))

