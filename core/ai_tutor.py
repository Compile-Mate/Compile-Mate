"""
AI Code Tutor - Powered by OpenAI
Provides intelligent hints and explanations for coding problems
"""

import openai
from django.conf import settings
from typing import Dict, List, Optional
import json


class AICodeTutor:
    """AI-powered code tutor using OpenAI GPT-4."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"
    
    def get_hint(self, problem_description: str, user_code: str, hint_level: int = 1) -> Dict:
        """
        Get a progressive hint for the problem.
        
        Args:
            problem_description: The problem statement
            user_code: User's current code attempt
            hint_level: 1 (gentle), 2 (moderate), 3 (detailed)
        
        Returns:
            Dict with hint text and suggested approach
        """
        try:
            hint_prompts = {
                1: "Give a gentle hint without revealing the solution. Focus on the approach.",
                2: "Provide a moderate hint with some implementation details but don't write code.",
                3: "Give a detailed hint with pseudocode but not the complete solution."
            }
            
            system_prompt = """You are an expert programming tutor. Help students learn by providing 
            progressive hints that guide them toward the solution without giving it away completely. 
            Be encouraging and educational."""
            
            user_prompt = f"""Problem:
{problem_description}

Student's Current Code:
{user_code}

{hint_prompts.get(hint_level, hint_prompts[1])}

Format your response as JSON with these keys:
- hint: The hint text
- approach: Suggested approach or algorithm
- time_complexity: Expected time complexity
- key_concepts: List of 2-3 key concepts to understand
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'hint': result.get('hint', ''),
                'approach': result.get('approach', ''),
                'time_complexity': result.get('time_complexity', ''),
                'key_concepts': result.get('key_concepts', []),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hint': 'Unable to generate hint at this time. Please try again later.'
            }
    
    def explain_error(self, error_message: str, user_code: str, language: str) -> Dict:
        """
        Explain a runtime or compilation error.
        
        Args:
            error_message: The error message from execution
            user_code: User's code that caused the error
            language: Programming language
        
        Returns:
            Dict with explanation and fix suggestion
        """
        try:
            system_prompt = """You are a debugging expert. Explain errors in simple terms 
            and suggest fixes. Be concise and educational."""
            
            user_prompt = f"""Language: {language}

Code:
{user_code}

Error:
{error_message}

Explain what caused this error and how to fix it. Format as JSON with:
- explanation: What the error means
- cause: Why it happened
- fix: How to fix it (be specific)
- example: A corrected code snippet (if applicable)
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'explanation': result.get('explanation', ''),
                'cause': result.get('cause', ''),
                'fix': result.get('fix', ''),
                'example': result.get('example', ''),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def review_code(self, code: str, language: str, problem_description: str) -> Dict:
        """
        Review code and provide feedback on quality, efficiency, and style.
        
        Args:
            code: User's submitted code
            language: Programming language
            problem_description: The problem being solved
        
        Returns:
            Dict with review feedback
        """
        try:
            system_prompt = """You are a senior software engineer conducting a code review. 
            Provide constructive feedback on code quality, efficiency, readability, and best practices."""
            
            user_prompt = f"""Language: {language}

Problem:
{problem_description}

Code to Review:
{code}

Provide a comprehensive code review. Format as JSON with:
- rating: Overall rating 1-10
- strengths: List of 2-3 things done well
- improvements: List of 2-3 areas for improvement
- time_complexity: Actual time complexity
- space_complexity: Actual space complexity
- best_practices: List of best practices to follow
- optimized_approach: Suggestion for optimization (if applicable)
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'rating': result.get('rating', 5),
                'strengths': result.get('strengths', []),
                'improvements': result.get('improvements', []),
                'time_complexity': result.get('time_complexity', ''),
                'space_complexity': result.get('space_complexity', ''),
                'best_practices': result.get('best_practices', []),
                'optimized_approach': result.get('optimized_approach', ''),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_test_cases(self, problem_description: str, constraints: str = "") -> Dict:
        """
        Suggest additional test cases for a problem.
        
        Args:
            problem_description: The problem statement
            constraints: Problem constraints
        
        Returns:
            Dict with suggested test cases
        """
        try:
            system_prompt = """You are an expert at designing comprehensive test cases 
            that cover edge cases, boundary conditions, and common pitfalls."""
            
            user_prompt = f"""Problem:
{problem_description}

Constraints:
{constraints}

Generate 5 diverse test cases including edge cases. Format as JSON with:
- test_cases: List of objects with 'input', 'expected_output', and 'description' fields
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'test_cases': result.get('test_cases', []),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class AIProblemGenerator:
    """AI-powered problem generator."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"
    
    def generate_problem(
        self, 
        difficulty: str,
        topics: List[str],
        style: str = "competitive"
    ) -> Dict:
        """
        Generate a new coding problem.
        
        Args:
            difficulty: easy, medium, or hard
            topics: List of topics (e.g., ["arrays", "dynamic programming"])
            style: competitive, interview, or educational
        
        Returns:
            Dict with problem details
        """
        try:
            system_prompt = """You are an expert at creating engaging and educational 
            coding problems. Generate original problems that are clear, well-structured, 
            and have interesting storylines."""
            
            topics_str = ", ".join(topics)
            
            user_prompt = f"""Create a {difficulty} difficulty {style} programming problem.

Topics to cover: {topics_str}

Generate a complete problem with JSON format:
- title: Catchy problem title
- description: Full problem description with story/context
- input_format: Description of input format
- output_format: Description of output format
- constraints: List of constraints
- examples: List of 3 examples with input/output/explanation
- test_cases: List of 5 test cases with input/expected_output
- hints: List of 2-3 hints
- solution_approach: High-level approach to solve
- time_limit: Time limit in seconds (1-5)
- memory_limit: Memory limit in MB (128-512)
- tags: List of relevant tags
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'problem': result
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Initialize global instances
ai_tutor = AICodeTutor()
ai_problem_generator = AIProblemGenerator()

