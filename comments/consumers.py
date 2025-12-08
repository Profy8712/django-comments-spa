# comments/consumers.py
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
        """
        We do not expect messages from client right now,
        so this can stay empty or be used for debug.
        """
        return

    async def comment_created(self, event):
        """
        Called from CommentListCreateView.perform_create via channel_layer.group_send.
        event = {"type": "comment_created", "comment_id": <int>}
        """
        comment_id = event.get("comment_id")
        if comment_id is None:
            return

        # All ORM and serializer work must run in a sync thread
        data = await self._get_serialized_comment(comment_id)

        await self.send_json(
            {
                "type": "comment_created",
                "payload": data,
            }
        )

    @sync_to_async
    def _get_serialized_comment(self, comment_id: int) -> dict:
        comment = (
            Comment.objects.select_related("parent")
            .prefetch_related("attachments")
            .get(pk=comment_id)
        )
        return CommentSerializer(comment).data
