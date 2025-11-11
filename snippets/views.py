from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Snippet


@login_required
def snippet_list(request):
    """List all snippets."""
    my_snippets = Snippet.objects.filter(author=request.user).order_by('-created_at')
    public_snippets = Snippet.objects.filter(visibility='public').exclude(author=request.user).order_by('-created_at')[:20]
    
    context = {
        'my_snippets': my_snippets,
        'public_snippets': public_snippets,
    }
    return render(request, 'snippets/snippet_list.html', context)


@login_required
def snippet_create(request):
    """Create a new snippet."""
    if request.method == 'POST':
        title = request.POST.get('title')
        language = request.POST.get('language')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        Snippet.objects.create(
            author=request.user,
            title=title,
            language=language,
            code=code,
            description=description,
            visibility='public' if is_public else 'private'
        )
        
        messages.success(request, 'Snippet created successfully!')
        return redirect('snippets:list')
    
    return render(request, 'snippets/snippet_create.html')


@login_required
def snippet_detail(request, snippet_id):
    """View snippet details."""
    snippet = get_object_or_404(Snippet, id=snippet_id)
    
    if snippet.visibility == 'private' and snippet.author != request.user:
        messages.error(request, 'You do not have permission to view this snippet.')
        return redirect('snippets:list')
    
    # Increment views
    snippet.views += 1
    snippet.save()
    
    context = {'snippet': snippet}
    return render(request, 'snippets/snippet_detail.html', context)


@login_required
def snippet_delete(request, snippet_id):
    """Delete a snippet."""
    snippet = get_object_or_404(Snippet, id=snippet_id, author=request.user)
    snippet.delete()
    messages.success(request, 'Snippet deleted successfully!')
    return redirect('snippets:list')
