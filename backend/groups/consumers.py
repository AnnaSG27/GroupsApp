import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f"group_{self.group_id}"

        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # broadcast to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': data
            }
        )

    # handler for messages sent to group
    async def chat_message(self, event):
        message = event['message']
        # send message back to WebSocket
        await self.send(text_data=json.dumps(message))
