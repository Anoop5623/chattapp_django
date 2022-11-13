from django.urls import path
from .consumer import *
ws_patttern = [
   # path('ws_test', MyConsumer.as_asgi()),
    path('group/<str:groupname>/', MysyncConsumer.as_asgi()),  
    path('chat/<str:groupname>/', MychatConsumer.as_asgi()),  
    path('notification/<str:groupname>/', Notifications.as_asgi()), 
   # path('ws_test', MyasyncConsumer.as_asgi()),
]
