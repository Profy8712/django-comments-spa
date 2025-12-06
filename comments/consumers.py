import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.renderers import JSONRenderer

from .models import Comment
from .serializers import CommentSerializer


class CommentsConsumer(AsyncWebsocketConsumer):
    group_name = "comments"

    async def connect(self):
        """Handle WebSocket connection."""
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Client messages are not used in this simple example."""
        return

    async def comment_created(self, event):
        """Handle 'comment_created' event from backend."""
        comment_id = event.get("comment_id")
        comment = await sync_to_async(Comment.objects.get)(pk=comment_id)
        serializer = CommentSerializer(comment)
        data = serializer.data

        await self.send(text_data=json.dumps({"type": "comment_created", "comment": data}))
