import os
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from apps.projects.consumers import TaskConsumer


class AutoLoginWSMiddleware:
    """WebSocket 自动认证：本地单用户模式"""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from apps.accounts.middleware import get_default_user
        from asgiref.sync import sync_to_async
        scope['user'] = await sync_to_async(get_default_user)()
        return await self.inner(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AutoLoginWSMiddleware(
            URLRouter([
                path("ws/task/<str:task_id>/", TaskConsumer.as_asgi()),
            ])
        )
    ),
})
