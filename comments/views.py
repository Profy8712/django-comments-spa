from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from rest_framework import filters, generics, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .documents import CommentDocument
from .models import Comment
from .serializers import (
    AttachmentCreateSerializer,
    AttachmentSerializer,
    CommentSearchResultSerializer,
    CommentSerializer,
)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET: List root comments (with nested children via prefetch).
    POST: Create a new comment (captcha required).
    """

    serializer_class = CommentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["user_name", "email", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Comment.objects.filter(parent__isnull=True)
            .select_related("parent")
            .prefetch_related(
                "attachments",
                "children",
                "children__attachments",
                "children__children",
                "children__children__attachments",
            )
        )

    def perform_create(self, serializer):
        comment = serializer.save()

        # notify all websocket clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments",
            {"type": "comment_created", "comment_id": comment.id},
        )


class CommentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single comment (with attachments and nested children prefetch).
    """

    queryset = Comment.objects.all().prefetch_related(
        "attachments",
        "children",
        "children__attachments",
        "children__children",
        "children__children__attachments",
    )
    serializer_class = CommentSerializer


class CaptchaAPIView(APIView):
    """
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
    POST /api/comments/<pk>/upload/
    Upload a single attachment for an existing comment.
    """

    serializer_class = AttachmentCreateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        comment_id = kwargs.get("pk")

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["comment"] = comment.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(AttachmentSerializer(instance).data, status=status.HTTP_201_CREATED)


class CommentSearchAPIView(APIView):
    """
    GET /api/search/comments/?q=...
    Elasticsearch search: text, user_name, email.
    """

    serializer_class = CommentSearchResultSerializer

    def get(self, request, *args, **kwargs):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"detail": "Query param 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        search = (
            CommentDocument.search()
            .query(
                "multi_match",
                query=q,
                fields=["text", "user_name", "email"],
                fuzziness="AUTO",
            )
            .extra(track_total_hits=True)[:50]
        )

        res = search.execute()

        items = [
            {
                "id": int(hit.id),
                "user_name": getattr(hit, "user_name", None),
                "email": getattr(hit, "email", None),
                "text": getattr(hit, "text", None),
                "created_at": getattr(hit, "created_at", None),
            }
            for hit in res
        ]

        data = self.serializer_class(items, many=True).data

        total = getattr(res.hits, "total", None)
        total_value = getattr(total, "value", len(items)) if total else len(items)

        return Response({"query": q, "count": total_value, "results": data}, status=status.HTTP_200_OK)
