from multiprocessing.util import is_abstract_socket_namespace
from operator import ipow
from urllib import request
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from time import sleep
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
import asyncio
import json
from channels.layers import get_channel_layer
from .models import *
channel_layer = get_channel_layer()


class MysyncConsumer(SyncConsumer):
   
    def websocket_connect(self, event):
        print("websocket connected", event['type'])
       
        if event['type'] == "websocket.connect":
            self.old = 1
        self.groupname = self.scope['url_route']['kwargs']['groupname']
        async_to_sync(self.channel_layer.group_add)(
            self.groupname, self.channel_name)
        self.send({
            'type': 'websocket.accept',
            'text': "successfully connected"
        })
        self.chat_message(event)
        

    def websocket_receive(self, event):
        print("message from client", event['text'])
        group = Group.objects.get(group_name=self.groupname)
        message = json.loads(event['text'])
        user = User.objects.get(username=message['sender'])
        
        group_messages.objects.create(parent_group=group,parent_user=user,message_text=message['msg'])
        async_to_sync(self.channel_layer.group_send)(
            self.groupname,
            {
                "type": "chat.message",
                "text": event['text'],
            },
        )

    def chat_message(self, event):
        print(" chat message event...", event)
    
        # user = User.objects.get(username=self.curuser)
        # unseen_notifications=Notification.unseen_notification(user_to=user)
        if self.old == 1:
            messages = Group.last_messages(grp_name=self.groupname)
            for i in messages:
                old_msg = {
                    "msg": i.message_text,
                    "sender": str(i.parent_user),
                    # "unseen":unseen_notifications
                }

                self.send({
                    'type': 'websocket.send',
                    'text': str(json.dumps(old_msg))
                })

            self.old = 0
        else:
            # msg=json.loads(event['text'])
            # msg["unseen"]=unseen_notifications
            self.send({
                'type': 'websocket.send',
                'text': event["text"]
                # 'text': str(json.dumps(msg))
            })

    def websocket_disconnect(self, event):
        print("disconnect", event)
        async_to_sync(self.channel_layer.group_discard)(
            self.groupname, self.channel_name)
        raise StopConsumer()




class MychatConsumer(SyncConsumer):
    def websocket_connect(self, event):
        print("websocket connected", event['type'])
        if event['type'] == "websocket.connect":
            self.old = 1
        self.groupname = self.scope['url_route']['kwargs']['groupname']
        async_to_sync(self.channel_layer.group_add)(
            self.groupname, self.channel_name)
        self.send({
            'type': 'websocket.accept',
            'text': "successfully connected"
        })
        self.chat_message(event)
        

    def websocket_receive(self, event):
        print("message from client", event['text'])
        room = One_to_one_room.objects.get(group_name=self.groupname)
        message = json.loads(event['text'])
        print(event['text'])
        user1 = User.objects.get(username=message['sender'])
        user2 = User.objects.get(username=message['send_to'])
        personal_messages.objects.create(message_by=user1,message_to=user2,message_text=message['msg'], chat_room =room)
        async_to_sync(self.channel_layer.group_send)(
            self.groupname,
            {
                "type": "chat.message",
                "text": event['text'],
            },
        )
        
  #onetoone
    def chat_message(self, event):
         print(" chat message event...", event)
         
         if self.old == 1:
            messages  =personal_messages.last_messages(grp_name=self.groupname)
            for message in messages:
                old_msg = {
                     "msg": message.message_text,
                     "sender": str(message.message_by)
                 }

                self.send({
                    'type': 'websocket.send',
                     'text': str(json.dumps(old_msg))
                 })

            self.old = 0
         else:
            self.send({
                'type': 'websocket.send',
                'text': event["text"]
            })

    def websocket_disconnect(self, event):
        print("disconnect", event)
        async_to_sync(self.channel_layer.group_discard)(
            self.groupname, self.channel_name)
        raise StopConsumer()


class Notifications(SyncConsumer):
    def websocket_connect(self, event):
        print("websocket connected", event['type'])
        self.date=0
        self.groupname = self.scope['url_route']['kwargs']['groupname']
        if event['type'] == "websocket.connect":
            self.old = 1
        async_to_sync(self.channel_layer.group_add)(
            self.groupname, self.channel_name)
        self.send({
            'type': 'websocket.accept',
            'text': "successfully connected"
        })
        self.chat_notification(event)
        

    def websocket_receive(self, event):
        print("message from client", event['text'])
        async_to_sync(self.channel_layer.group_send)(
            self.groupname,
            {
                "type": "chat.notification",
                "text": event['text'],
            },
        )

    def chat_notification(self, event):
        userr=User.objects.get(username=self.groupname)
        notification=Notification()
        if self.old == 1:
            notification=Notification.last_notifications(userr) 
            self.old = 0 
        else:
            notification=Notification.latest_notifications(userr,self.date)
        if notification.exists():
            self.date=notification[0].date_posted
            group_or_contacts=0
            for notify in notification:
                if notify.is_group:
                    group_or_contacts= notify.group.group_name
                else:
                    group_or_contacts=notify.notify_by.username
                mssg={
                        "msg":notify.notification_text,
                        "date":str(notify.date_posted),
                        "is_group":notify.is_group,
                        "group_or__contact":group_or_contacts,
                        "is_seen": notify.is_seen
                        }
                self.send({
                        'type': 'websocket.send',
                        'text': str(json.dumps(mssg))
             })
# await is to call asynchronous functions
# send group_send group_ add are asynch function to use thems we use asynch to synch

    def websocket_disconnect(self, event):
        print("disconnect", event)
        async_to_sync(self.channel_layer.group_discard)(
            self.groupname, self.channel_name)
        raise StopConsumer()

