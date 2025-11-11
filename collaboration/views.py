from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollaborationRoom
import uuid


@login_required
def room_list(request):
    """List all active collaboration rooms."""
    active_rooms = CollaborationRoom.objects.filter(is_active=True)
    my_rooms = CollaborationRoom.objects.filter(host=request.user)
    
    context = {
        'active_rooms': active_rooms,
        'my_rooms': my_rooms,
    }
    return render(request, 'collaboration/room_list.html', context)


@login_required
def create_room(request):
    """Create a new collaboration room."""
    if request.method == 'POST':
        name = request.POST.get('name', f"{request.user.username}'s Room")
        room_type = request.POST.get('room_type', 'full')
        
        room = CollaborationRoom.objects.create(
            name=name,
            room_type=room_type,
            host=request.user
        )
        room.participants.add(request.user)
        
        messages.success(request, f'Room created: {name}')
        return redirect('collaboration:room', room_id=room.room_id)
    
    return render(request, 'collaboration/create_room.html')


@login_required
def room_view(request, room_id):
    """View and join a collaboration room."""
    room = get_object_or_404(CollaborationRoom, room_id=room_id, is_active=True)
    
    # Add user to participants if not already
    if request.user not in room.participants.all():
        if room.participants.count() >= room.max_participants:
            messages.error(request, 'Room is full!')
            return redirect('collaboration:list')
        room.participants.add(request.user)
    
    context = {
        'room': room,
        'is_host': request.user == room.host,
    }
    return render(request, 'collaboration/room.html', context)


@login_required
def leave_room(request, room_id):
    """Leave a collaboration room."""
    room = get_object_or_404(CollaborationRoom, room_id=room_id)
    room.participants.remove(request.user)
    
    messages.success(request, 'Left the room')
    return redirect('collaboration:list')
