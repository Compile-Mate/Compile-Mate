"""
AI-powered problem recommendation system for CompileMate.
Uses collaborative filtering and content-based recommendations.
"""

from django.db.models import Q, Count, Avg
from django.core.cache import cache
from collections import defaultdict
import random


class ProblemRecommender:
    """Intelligent problem recommendation engine."""
    
    def __init__(self, user):
        self.user = user
    
    def get_recommendations(self, limit=10):
        """
        Get personalized problem recommendations for the user.
        Uses multiple strategies:
        1. Difficulty-based (slightly harder than current level)
        2. Topic-based (similar to solved problems)
        3. Collaborative filtering (what similar users solved)
        4. Trending problems
        """
        
        # Check cache first
        cache_key = f"recommendations:{self.user.id}"
        cached_recommendations = cache.get(cache_key)
        if cached_recommendations:
            return cached_recommendations
        
        recommendations = []
        
        # Get user's solved problems
        from problems.models import Submission, Problem
        solved_problem_ids = Submission.objects.filter(
            user=self.user,
            status='accepted'
        ).values_list('problem_id', flat=True).distinct()
        
        # Strategy 1: Difficulty-based recommendations (40% weight)
        difficulty_recs = self._get_difficulty_based_recommendations(solved_problem_ids, limit=4)
        recommendations.extend(difficulty_recs)
        
        # Strategy 2: Topic-based recommendations (30% weight)
        topic_recs = self._get_topic_based_recommendations(solved_problem_ids, limit=3)
        recommendations.extend(topic_recs)
        
        # Strategy 3: Collaborative filtering (20% weight)
        collab_recs = self._get_collaborative_recommendations(solved_problem_ids, limit=2)
        recommendations.extend(collab_recs)
        
        # Strategy 4: Trending problems (10% weight)
        trending_recs = self._get_trending_problems(solved_problem_ids, limit=1)
        recommendations.extend(trending_recs)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for problem in recommendations:
            if problem.id not in seen:
                seen.add(problem.id)
                unique_recommendations.append(problem)
        
        # Limit to requested number
        final_recommendations = unique_recommendations[:limit]
        
        # Cache for 1 hour
        cache.set(cache_key, final_recommendations, 3600)
        
        return final_recommendations
    
    def _get_difficulty_based_recommendations(self, solved_ids, limit=4):
        """Recommend problems based on user's skill level."""
        from problems.models import Problem, Submission
        
        # Calculate user's proficiency by difficulty
        user_stats = Submission.objects.filter(
            user=self.user,
            status='accepted'
        ).values('problem__difficulty').annotate(count=Count('problem', distinct=True))
        
        difficulty_counts = {stat['problem__difficulty']: stat['count'] for stat in user_stats}
        
        # Determine next difficulty level
        easy_count = difficulty_counts.get('easy', 0)
        medium_count = difficulty_counts.get('medium', 0)
        hard_count = difficulty_counts.get('hard', 0)
        
        # Progressive difficulty
        if easy_count < 10:
            target_difficulty = 'easy'
        elif medium_count < 20:
            target_difficulty = 'medium'
        else:
            target_difficulty = 'hard'
        
        # Get problems of target difficulty
        problems = Problem.objects.filter(
            status='published',
            difficulty=target_difficulty
        ).exclude(
            id__in=solved_ids
        ).order_by('-acceptance_rate')[:limit]
        
        return list(problems)
    
    def _get_topic_based_recommendations(self, solved_ids, limit=3):
        """Recommend problems with similar tags to what user has solved."""
        from problems.models import Problem
        
        # Get tags from user's solved problems
        user_tags = Problem.objects.filter(
            id__in=solved_ids
        ).values_list('tags__id', flat=True)
        
        if not user_tags:
            # Return popular problems if no history
            return list(Problem.objects.filter(
                status='published'
            ).exclude(
                id__in=solved_ids
            ).order_by('-total_submissions')[:limit])
        
        # Find problems with similar tags
        problems = Problem.objects.filter(
            status='published',
            tags__id__in=user_tags
        ).exclude(
            id__in=solved_ids
        ).annotate(
            tag_match_count=Count('tags')
        ).order_by('-tag_match_count', '-acceptance_rate')[:limit]
        
        return list(problems)
    
    def _get_collaborative_recommendations(self, solved_ids, limit=2):
        """Recommend problems based on what similar users solved."""
        from problems.models import Problem, Submission
        from users.models import User
        
        if not solved_ids:
            return []
        
        # Find users who solved similar problems
        similar_users = User.objects.filter(
            submissions__problem_id__in=solved_ids,
            submissions__status='accepted'
        ).exclude(
            id=self.user.id
        ).annotate(
            common_problems=Count('submissions__problem', distinct=True)
        ).filter(
            common_problems__gte=3  # At least 3 problems in common
        ).order_by('-common_problems')[:20]
        
        if not similar_users:
            return []
        
        # Get problems solved by similar users but not by current user
        similar_user_ids = [user.id for user in similar_users]
        problems = Problem.objects.filter(
            submissions__user_id__in=similar_user_ids,
            submissions__status='accepted',
            status='published'
        ).exclude(
            id__in=solved_ids
        ).annotate(
            popularity=Count('submissions__user', distinct=True)
        ).order_by('-popularity')[:limit]
        
        return list(problems)
    
    def _get_trending_problems(self, solved_ids, limit=1):
        """Get currently trending problems."""
        from problems.models import Problem
        from django.utils import timezone
        from datetime import timedelta
        
        # Get problems with most submissions in last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        problems = Problem.objects.filter(
            status='published',
            submissions__submitted_at__gte=week_ago
        ).exclude(
            id__in=solved_ids
        ).annotate(
            recent_submissions=Count('submissions')
        ).order_by('-recent_submissions')[:limit]
        
        return list(problems)
    
    def get_daily_challenge(self):
        """Get a daily challenge problem for the user."""
        cache_key = f"daily_challenge:{self.user.id}:{timezone.now().date()}"
        cached_challenge = cache.get(cache_key)
        
        if cached_challenge:
            return cached_challenge
        
        # Get a problem at user's level
        from problems.models import Problem, Submission
        
        solved_ids = Submission.objects.filter(
            user=self.user,
            status='accepted'
        ).values_list('problem_id', flat=True)
        
        # Determine user level
        solved_count = len(solved_ids)
        if solved_count < 10:
            difficulty = 'easy'
        elif solved_count < 30:
            difficulty = 'medium'
        else:
            difficulty = random.choice(['medium', 'hard'])
        
        # Get random problem of that difficulty
        problems = list(Problem.objects.filter(
            status='published',
            difficulty=difficulty
        ).exclude(id__in=solved_ids))
        
        if problems:
            challenge = random.choice(problems)
            # Cache for 24 hours
            cache.set(cache_key, challenge, 86400)
            return challenge
        
        return None
    
    def get_similar_problems(self, problem, limit=5):
        """Get problems similar to a given problem."""
        from problems.models import Problem
        
        # Get problems with similar tags
        similar = Problem.objects.filter(
            tags__in=problem.tags.all(),
            status='published',
            difficulty=problem.difficulty
        ).exclude(
            id=problem.id
        ).annotate(
            tag_match_count=Count('tags')
        ).order_by('-tag_match_count', '-acceptance_rate')[:limit]
        
        return list(similar)

