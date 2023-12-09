# chat/routing.py
"""
Adapted from
https://channels.readthedocs.io/en/latest/tutorial/index.html
"""

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/playing", consumers.ChatConsumer.as_asgi()),
]