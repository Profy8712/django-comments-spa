from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Comment
from .serializers import CommentSerializer


class CommentsConsumer(AsyncJsonWebsocketConsumer):
    group_name = "comments"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Client -> server messages are not required now
        return

    async def comment_created(self, event):
        """
        event = {"type": "comment_created", "comment_id": <int>}
        """
        comment_id = event.get("comment_id")
        if not comment_id:
            return

        data = await self._get_serialized_comment(comment_id)
        if data is None:
            return

        await self.send_json({"type": "comment_created", "payload": data})

    @sync_to_async
    def _get_serialized_comment(self, comment_id: int):
        try:
            comment = (
                Comment.objects.select_related("parent")
                .prefetch_related("attachments", "children")
                .get(pk=comment_id)
            )
        except Comment.DoesNotExist:
            return None

        return CommentSerializer(comment).data
