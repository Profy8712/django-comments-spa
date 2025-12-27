from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from rest_framework import filters, generics, parsers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .documents import CommentDocument
from .models import Attachment, Comment
from .permissions import IsStaffOrSuperuser
from .serializers import (
    AttachmentCreateSerializer,
    AttachmentSerializer,
    AttachmentUploadSerializer,
    CommentCreateSerializer,
    CommentSearchResultSerializer,
    CommentSerializer,
)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET: public
    POST:
      - anonymous -> allowed, CAPTCHA required (handled in serializer)
      - JWT user  -> allowed, CAPTCHA not required
    """
    serializer_class = CommentSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentSerializer
    permission_classes = [AllowAny]

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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        comment = serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments",
            {"type": "comment_created", "comment_id": comment.id},
        )


class CommentDetailView(generics.RetrieveAPIView):
    """
    GET: public
    """
    queryset = Comment.objects.all().prefetch_related(
        "attachments",
        "children",
        "children__attachments",
        "children__children",
        "children__children__attachments",
    )
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class CaptchaAPIView(APIView):
    """
    GET /api/comments/captcha/
    -> { "key": "<hash>", "image": "/captcha/image/<hash>/" }
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        key = CaptchaStore.generate_key()
        url = captcha_image_url(key)
        return Response({"key": key, "image": url}, status=status.HTTP_200_OK)



class AttachmentTempUploadView(generics.CreateAPIView):
    """
    Upload attachments WITHOUT comment id (JWT only).
    POST /api/comments/upload/
    Response: { id, file, upload_key, uploaded_at }
    """
    serializer_class = AttachmentUploadSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        f = request.FILES.get("file")
        if not f:
            return Response({"file": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        instance = Attachment.objects.create(file=f)
        return Response(AttachmentUploadSerializer(instance).data, status=status.HTTP_201_CREATED)

class AttachmentUploadView(generics.CreateAPIView):
    """
    Upload attachments ONLY with JWT.
    """
    serializer_class = AttachmentCreateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [IsAuthenticated]

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
    Public endpoint.
    """
    serializer_class = CommentSearchResultSerializer
    permission_classes = [AllowAny]

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


class AdminCommentDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/comments/admin/comments/<id>/
    Admin-only endpoint for deleting comments.
    """
    queryset = Comment.objects.all()
    permission_classes = [IsStaffOrSuperuser]

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()

        # Optional hardening:
        # forbid deleting comments that have replies
        # if comment.children.exists():
        #     return Response(
        #         {"detail": "Cannot delete comment with replies."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        return super().delete(request, *args, **kwargs)
