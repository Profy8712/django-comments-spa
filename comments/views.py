from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from rest_framework import generics, filters, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Attachment
from .serializers import (
    CommentSerializer,
    AttachmentSerializer,
    AttachmentCreateSerializer,
)


class CommentListCreateView(generics.ListCreateAPIView):
    """List all comments or create a new comment."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user_name", "email", "created_at"]
    ordering = ["-created_at"]  # LIFO

    def perform_create(self, serializer):
        comment = serializer.save()

        # WS notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments",
            {
                "type": "comment_created",
                "comment_id": comment.id,
            },
        )


class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CaptchaAPIView(APIView):
    """SPA service – returns key + image url."""

    def get(self, request, *args, **kwargs):
        key = CaptchaStore.generate_key()
        url = captcha_image_url(key)

        return Response(
            {
                "key": key,
                "image": url,
            }
        )


class AttachmentUploadView(generics.CreateAPIView):
    """
    Upload a single attachment for an existing comment.
    POST /api/comments/<pk>/upload/
    """

    serializer_class = AttachmentCreateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        comment_id = kwargs.get("pk")

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["comment"] = comment.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
