from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send chat history
        past_messages = await self.get_past_messages(self.thread_id)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': past_messages
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

        saved_message = await self.save_message(self.thread_id, sender_username, message)
        if not saved_message:
            await self.send(text_data=json.dumps({
                'error': 'Invalid thread or user'
            }))
            return

        # Broadcast to all clients in this thread
        await self.channel_layer.group_send(
            self.room_group_name,
            {
        'type': 'chat_message',
        'id': saved_message.id,
        'message': saved_message.content,
        'sender': saved_message.sender.username,
        'receiver': saved_message.receiver.username,
        'timestamp': saved_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_past_messages(self, thread_id):
        from .models import Thread, Message
        try:
            thread = Thread.objects.get(id=thread_id)
            messages = Message.objects.filter(thread=thread).order_by('timestamp')[:50]
            return [
                {
                    'id': msg.id,
                    'sender': msg.sender.username,
                    'receiver': msg.receiver.username,  # ✅ include receiver
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ][::-1]
        except Thread.DoesNotExist:
            return []

    @database_sync_to_async
    def get_thread(self, thread_id):
        from .models import Thread
        return Thread.objects.get(id=thread_id)

    
    @database_sync_to_async
    def save_message(self, thread_id, sender_username, content):
      from .models import Thread, Message
      User = get_user_model()

      try:
        thread = Thread.objects.get(id=thread_id)
        sender = User.objects.get(username=sender_username)

        # ✅ Correctly determine the receiver (the other participant)
        if thread.user1 == sender:
            receiver = thread.user2
        else:
            receiver = thread.user1

        # ✅ Save message with correct sender & receiver
        msg = Message.objects.create(
            thread=thread,
            sender=sender,
            receiver=receiver,
            content=content
        )
        return msg

      except (Thread.DoesNotExist, User.DoesNotExist):
        return None

