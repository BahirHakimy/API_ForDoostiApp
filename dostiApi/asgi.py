import os
import django
from django.utils.encoding import force_str

django.utils.encoding.force_text = force_str
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dostiApi.production")
django.setup()
import chat.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns)),
    }
)
