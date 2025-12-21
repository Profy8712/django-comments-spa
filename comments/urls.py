from django.urls import path

from .views import (
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

    # comment detail endpoints
    path("<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("<int:pk>/upload/", AttachmentUploadView.as_view(), name="comment-upload"),
]
