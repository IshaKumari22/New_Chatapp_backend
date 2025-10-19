from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model

# User=get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        past_messages=await self.get_past_messages(self.thread_id)
        await self.send(text_data=json.dumps({
            'type':'chat_history',
            'messages':past_messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']

        saved_message=await self.save_message(self.thread_id,sender_username,message)
        if not saved_message:
            await self.send(text_data=json.dumps({
                'error':'Invalid thread or user'
            }))
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id':saved_message.id,
                'message':saved_message.content,             
                'sender': sender_username,
                'timestamp':saved_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_past_messages(self,thread_id):
        from .models import Thread,Message
        try:
            thread=Thread.objects.get(id=thread_id)
            messages=Message.objects.filter(thread=thread).order_by('timestamp')[:50]
            return[
                {
                    'id':msg.id,
                    'sender':msg.sender.username,
                    'content':msg.content,
                    'timestamp':msg.timestamp.isoformat()
                }
                for msg in messages
            ][::-1]
        except Thread.DoesNotExist:
            return[]
    @database_sync_to_async
    def get_thread(self,thread_id):
        from .models import Thread
        return Thread.objects.get(id=thread_id)
    
    @database_sync_to_async
    def save_message(self,thread_id,sender_username,content):
        from .models import Thread,Message
        try:
            thread=Thread.objects.get(id=thread_id)
            sender=get_user_model().objects.get(username=sender_username)
            return Message.objects.create(thread=thread,sender=sender,content=content)
        except (Thread.DoesNotExist, get_user_model().DoesNotExist):
            return None
