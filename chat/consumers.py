import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        if not await self.user_can_access_room(user, self.room_id):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        if not message_content:
            return

        user = self.scope['user']
        message = await self.save_message(user, self.room_id, message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': user.id,
                'sender_name': user.full_name,
                'message_id': message.id,
                'timestamp': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def user_can_access_room(self, user, room_id):
        from .models import ChatRoom
        try:
            room = ChatRoom.objects.select_related('inquiry__tenant', 'inquiry__listing__owner').get(pk=room_id)
            return user in [room.inquiry.tenant, room.inquiry.listing.owner]
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        from .models import ChatRoom, Message
        room = ChatRoom.objects.get(pk=room_id)
        return Message.objects.create(room=room, sender=user, content=content)
