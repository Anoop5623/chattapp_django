"""
ASGI config for chattapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from home.routing import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chattapp.setting')

application = ProtocolTypeRouter(
    {"http": get_asgi_application(),
     "websocket": URLRouter(ws_patttern)
     }
)