# comments/urls.py
from django.urls import path

from .views import (
    CommentListCreateView,
    CommentDetailView,
    CaptchaAPIView,
    AttachmentUploadView,
)

app_name = "comments"

urlpatterns = [
    # /api/comments/
    path(
        "",
        CommentListCreateView.as_view(),
        name="comment-list",
    ),

    # /api/comments/<pk>/
    path(
        "<int:pk>/",
        CommentDetailView.as_view(),
        name="comment-detail",
    ),

    # /api/comments/<pk>/upload/
    path(
        "<int:pk>/upload/",
        AttachmentUploadView.as_view(),
        name="comment-upload",
    ),

    # optional: /api/comments/captcha/
    # you can keep this or remove it if you only use /api/captcha/
    path(
        "captcha/",
        CaptchaAPIView.as_view(),
        name="captcha",
    ),
]
