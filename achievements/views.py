"""
Views for Achievement & Badge System
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q

from .models import (
    Achievement, Badge, BadgeCategory, Milestone, 
    UserAchievement, UserBadge, UserMilestone, BadgeProgress
)


@login_required
def achievement_list(request):
    """Display all achievements and user's progress."""
    # Get all achievements
    all_achievements = Achievement.objects.order_by('-xp_reward', '-coin_reward')
    
    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement')
    
    user_achievement_ids = user_achievements.values_list('achievement_id', flat=True)
    
    # Categorize achievements
    unlocked_achievements = all_achievements.filter(id__in=user_achievement_ids)
    locked_achievements = all_achievements.exclude(id__in=user_achievement_ids)
    
    # Get user's badges
    user_badges = UserBadge.objects.filter(
        user=request.user
    ).select_related('badge')
    
    # Get badge progress
    badge_progress = BadgeProgress.objects.filter(
        user=request.user
    ).select_related('badge')
    
    # Calculate stats
    total_achievements = all_achievements.count()
    unlocked_count = unlocked_achievements.count()
    completion_rate = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0
    total_points = sum([ua.achievement.xp_reward for ua in user_achievements]) if user_achievements else 0
    
    context = {
        'unlocked_achievements': unlocked_achievements,
        'locked_achievements': locked_achievements,
        'user_badges': user_badges,
        'badge_progress': badge_progress,
        'total_achievements': total_achievements,
        'unlocked_count': unlocked_count,
        'completion_rate': completion_rate,
        'total_points': total_points,
    }
    return render(request, 'achievements/achievement_list.html', context)


@login_required
def badge_showcase(request):
    """Display user's badge showcase."""
    # Get all badge categories
    categories = BadgeCategory.objects.prefetch_related('badges')
    
    # Get user's badges
    user_badges = UserBadge.objects.filter(
        user=request.user
    ).select_related('badge')
    
    user_badge_ids = user_badges.values_list('badge_id', flat=True)
    
    # Get badge progress
    badge_progress_dict = {
        bp.badge_id: bp 
        for bp in BadgeProgress.objects.filter(user=request.user).select_related('badge')
    }
    
    # Organize badges by category
    category_data = []
    for category in categories:
        badges = category.badges.all()
        category_info = {
            'category': category,
            'badges': [],
            'unlocked_count': 0,
            'total_count': badges.count(),
        }
        
        for badge in badges:
            badge_info = {
                'badge': badge,
                'unlocked': badge.id in user_badge_ids,
                'progress': badge_progress_dict.get(badge.id),
            }
            category_info['badges'].append(badge_info)
            if badge_info['unlocked']:
                category_info['unlocked_count'] += 1
        
        category_data.append(category_info)
    
    context = {
        'category_data': category_data,
        'total_badges': sum(cat['total_count'] for cat in category_data),
        'unlocked_badges': sum(cat['unlocked_count'] for cat in category_data),
    }
    return render(request, 'achievements/badge_showcase.html', context)


@login_required
def milestones(request):
    """Display milestones and user's progress."""
    # Get all milestones
    all_milestones = Milestone.objects.order_by('type', 'target_value')
    
    # Get user's milestones
    user_milestones = UserMilestone.objects.filter(
        user=request.user
    ).select_related('milestone')
    
    user_milestone_ids = user_milestones.values_list('milestone_id', flat=True)
    
    # Organize milestones by type
    milestone_types = {}
    for milestone in all_milestones:
        if milestone.type not in milestone_types:
            milestone_types[milestone.type] = {
                'label': milestone.get_type_display(),
                'milestones': [],
            }
        
        milestone_info = {
            'milestone': milestone,
            'achieved': milestone.id in user_milestone_ids,
            'user_milestone': user_milestones.filter(milestone=milestone).first(),
        }
        milestone_types[milestone.type]['milestones'].append(milestone_info)
    
    context = {
        'milestone_types': milestone_types,
    }
    return render(request, 'achievements/milestones.html', context)
