from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from rest_framework import generics, filters, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Attachment
from .serializers import CommentSerializer, AttachmentCreateSerializer


class CommentListCreateView(generics.ListCreateAPIView):
    """List all comments or create a new comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # Sorting functionality
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user_name", "email", "created_at"]
    ordering = ["-created_at"]  # LIFO by default

    def perform_create(self, serializer):
        """Save comment and notify WebSocket group."""
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
    """Retrieve a single comment by ID."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CaptchaAPIView(APIView):
    """Return a new CAPTCHA for SPA client."""

    def get(self, request, *args, **kwargs):
        new_key = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_key)
        return Response(
            {
                "captcha_key": new_key,
                "captcha_image_url": image_url,
            }
        )


class AttachmentUploadView(generics.CreateAPIView):
    """Upload a single attachment for a given comment."""
    serializer_class = AttachmentCreateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        comment_id = kwargs.get("pk")

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["comment"] = comment.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
