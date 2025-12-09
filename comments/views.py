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
    """
    List root comments (with nested children) or create a new comment.
    """

    serializer_class = CommentSerializer

    # Sorting options for root comments
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user_name", "email", "created_at"]
    ordering = ["-created_at"]  # default LIFO

    def get_queryset(self):
        """
        Return only root comments (those without a parent),
        with related data preloaded to render the nested tree efficiently.
        """
        return (
            Comment.objects.filter(parent__isnull=True)
            .select_related()
            .prefetch_related(
                "attachments",
                "children",
                "children__attachments",
                "children__children",
                "children__children__attachments",
            )
        )

    def perform_create(self, serializer):
        """
        Save a new comment and notify all WebSocket subscribers.
        """
        comment = serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments",
            {
                "type": "comment_created",
                "comment_id": comment.id,
            },
        )


class CommentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single comment (with attachments and children).
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CaptchaAPIView(APIView):
    """
    JSON API for SPA – returns CAPTCHA key and image URL.

    GET /api/captcha/
    -> { "key": "<hash>", "image": "/captcha/image/<hash>/" }
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        key = CaptchaStore.generate_key()
        url = captcha_image_url(key)
        return Response({"key": key, "image": url}, status=status.HTTP_200_OK)


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
        instance = serializer.save()

        # serialize created attachment for response
        response_data = AttachmentSerializer(instance).data
        return Response(response_data, status=status.HTTP_201_CREATED)
