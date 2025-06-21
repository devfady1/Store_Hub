import os
import django
from django.core.asgi import get_asgi_application
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pages.routing

# ⭐ الإضافة دي
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(django_app),  # ⭐ دا اللي بيخدم الستاتيك
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pages.routing.websocket_urlpatterns
        )
    ),
})
