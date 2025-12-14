from django.urls import path

from .views import (
    AttachmentUploadView,
    CaptchaAPIView,
    CommentDetailView,
    CommentListCreateView,
    CommentSearchAPIView,
)

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/<int:pk>/upload/", AttachmentUploadView.as_view(), name="comment-upload"),

    path("captcha/", CaptchaAPIView.as_view(), name="captcha"),
    path("search/comments/", CommentSearchAPIView.as_view(), name="comment-search"),
]
