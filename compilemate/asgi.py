"""
ASGI config for compilemate project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

# Import the chat consumers
from core.consumers import ChatConsumer, AdminChatConsumer
# Import battle consumers
from battles.consumers import BattleConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compilemate.settings')

# WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
    path('ws/admin/chat/', AdminChatConsumer.as_asgi()),
    path('ws/battle/<uuid:battle_id>/', BattleConsumer.as_asgi()),
]

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
}) 