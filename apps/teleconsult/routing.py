from django.urls import re_path
from .consumers import VideoChatConsumer, ChatConsumer


websocket_urlpatterns = [
    re_path(r'^videochat/(?P<room_name>\w+)/$', VideoChatConsumer.as_asgi()),
    re_path(r'^text/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]