import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import SupportChat, ChatMessage, AdminAvailability
from django.utils import timezone

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        content = text_data_json.get('content', '')
        user_id = text_data_json.get('user_id')

        if message_type == 'message':
            # Save message to database
            message = await self.save_message(user_id, content)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'message_type': message.message_type,
                        'sender': message.sender.username,
                        'created_at': message.created_at.isoformat(),
                    }
                }
            )
        elif message_type == 'typing':
            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': user_id,
                    'is_typing': text_data_json.get('is_typing', False)
                }
            )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def save_message(self, user_id, content):
        user = User.objects.get(id=user_id)
        chat = SupportChat.objects.get(id=self.chat_id)
        
        message = ChatMessage.objects.create(
            chat=chat,
            sender=user,
            content=content,
            message_type='text'
        )
        
        # Update chat last activity
        chat.last_activity = timezone.now()
        chat.save()
        
        return message


class AdminChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.admin_id = self.scope['user'].id
        self.room_group_name = f'admin_{self.admin_id}'

        # Join admin room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'new_chat':
            # Notify admin of new chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_chat_notification',
                    'chat_id': text_data_json.get('chat_id'),
                    'subject': text_data_json.get('subject'),
                    'user': text_data_json.get('user')
                }
            )

    async def new_chat_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_chat',
            'chat_id': event['chat_id'],
            'subject': event['subject'],
            'user': event['user']
        })) 