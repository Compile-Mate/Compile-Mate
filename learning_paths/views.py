from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LearningPath, PathEnrollment


def path_list(request):
    """List all learning paths."""
    paths = LearningPath.objects.filter(is_published=True).order_by('-is_featured', '-enrolled_count')
    
    enrolled_paths = []
    if request.user.is_authenticated:
        enrolled_paths = PathEnrollment.objects.filter(user=request.user).values_list('learning_path_id', flat=True)
    
    context = {
        'paths': paths,
        'enrolled_paths': list(enrolled_paths),
    }
    return render(request, 'learning_paths/path_list.html', context)


def path_detail(request, slug):
    """View learning path details."""
    path = get_object_or_404(LearningPath.objects.prefetch_related('modules', 'topics'), slug=slug, is_published=True)
    
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = PathEnrollment.objects.get(user=request.user, learning_path=path)
            is_enrolled = True
        except PathEnrollment.DoesNotExist:
            pass
    
    context = {
        'path': path,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    }
    return render(request, 'learning_paths/path_detail.html', context)


@login_required
def enroll_path(request, slug):
    """Enroll in a learning path."""
    path = get_object_or_404(LearningPath, slug=slug, is_published=True)
    
    enrollment, created = PathEnrollment.objects.get_or_create(
        user=request.user,
        learning_path=path
    )
    
    if created:
        path.enrolled_count += 1
        path.save()
        messages.success(request, f'Successfully enrolled in {path.title}!')
    else:
        messages.info(request, 'You are already enrolled in this path.')
    
    return redirect('learning_paths:detail', slug=slug)


@login_required
def my_paths(request):
    """View user's enrolled paths."""
    enrollments = PathEnrollment.objects.filter(
        user=request.user
    ).select_related('learning_path').order_by('-enrolled_at')
    
    context = {'enrollments': enrollments}
    return render(request, 'learning_paths/my_paths.html', context)
