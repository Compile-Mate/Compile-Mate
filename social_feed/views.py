from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Follow
from users.models import User


@login_required
def feed(request):
    """View social feed."""
    # Get posts from followed users and own posts
    following = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(author_id__in=list(following) + [request.user.id]).select_related('author').order_by('-created_at')[:50]
    
    context = {'posts': posts}
    return render(request, 'social_feed/feed.html', context)


@login_required
def create_post(request):
    """Create a new post."""
    if request.method == 'POST':
        content = request.POST.get('content')
        post_type = request.POST.get('post_type', 'discussion')
        
        if content:
            Post.objects.create(
                author=request.user,
                content=content,
                post_type=post_type
            )
            messages.success(request, 'Post created!')
        
        return redirect('social_feed:feed')
    
    return redirect('social_feed:feed')


@login_required
def like_post(request, post_id):
    """Like/unlike a post."""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user already liked the post
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        post.likes_count -= 1
    else:
        post.likes.add(request.user)
        post.likes_count += 1
    
    post.save()
    return redirect('social_feed:feed')


@login_required
def add_comment(request, post_id):
    """Add comment to post."""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        
        if content:
            Comment.objects.create(
                author=request.user,
                post=post,
                content=content
            )
            post.comments_count += 1
            post.save()
        
    return redirect('social_feed:feed')


@login_required
def user_profile(request, username):
    """View user profile."""
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists() if request.user != profile_user else False
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'social_feed/profile.html', context)


@login_required
def follow_user(request, username):
    """Follow/unfollow a user."""
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('social_feed:profile', username=username)
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    
    if not created:
        follow.delete()
        messages.info(request, f'Unfollowed {username}')
    else:
        messages.success(request, f'Now following {username}!')
    
    return redirect('social_feed:profile', username=username)
