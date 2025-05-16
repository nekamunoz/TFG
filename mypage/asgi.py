import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

import chat.routing
import videochat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        chat.routing.websocket_urlpatterns +
        videochat.routing.websocket_urlpatterns
    )
})