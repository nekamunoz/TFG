from django.urls import re_path
from .consumers import VideoChatConsumer


websocket_urlpatterns = [
    re_path(r'', VideoChatConsumer.as_asgi()),
]