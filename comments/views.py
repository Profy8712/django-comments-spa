from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(generics.ListCreateAPIView):
    """List all comments or create a new comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # Sorting functionality
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user_name", "email", "created_at"]
    ordering = ["-created_at"]  # LIFO by default


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
