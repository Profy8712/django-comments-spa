from django.urls import path

from .views import (
    AttachmentTempUploadView,
    AdminCommentDeleteView,
    AttachmentUploadView,
    CaptchaAPIView,
    CommentDetailView,
    CommentListCreateView,
    CommentSearchAPIView,
)

urlpatterns = [
    path("", CommentListCreateView.as_view(), name="comment-list-create"),

    # service endpoints
    path("captcha/", CaptchaAPIView.as_view(), name="captcha"),
    path("search/", CommentSearchAPIView.as_view(), name="comment-search"),

    # admin endpoints
    path("admin/comments/<int:pk>/", AdminCommentDeleteView.as_view(), name="admin-comment-delete"),

    # comment detail endpoints
    path("upload/", AttachmentTempUploadView.as_view(), name="attachment-temp-upload"),

    path("<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("<int:pk>/upload/", AttachmentUploadView.as_view(), name="comment-upload"),
]
