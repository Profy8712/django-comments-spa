import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Initialize Django ASGI application first so that apps are loaded
django_asgi_app = get_asgi_application()

# Import routing only after Django has been set up
import comments.routing


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(comments.routing.websocket_urlpatterns)
        ),
    }
)
