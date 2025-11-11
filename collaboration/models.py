from django.db import models
from users.models import User
import uuid


class CollaborationRoom(models.Model):
    """Model for collaboration rooms."""
    
    ROOM_TYPE_CHOICES = [
        ('video', 'Video Call'),
        ('whiteboard', 'Whiteboard'),
        ('coding', 'Live Coding'),
        ('full', 'Full Suite'),
    ]
    
    room_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='full')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    participants = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.room_id}"


class RoomMessage(models.Model):
    """Model for chat messages in rooms."""
    
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
