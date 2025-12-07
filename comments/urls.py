from django.urls import path
from .views import (
    CommentListCreateView,
    CommentDetailView,
    CaptchaAPIView,
    AttachmentUploadView,
)

urlpatterns = [
    path("comments/", CommentListCreateView.as_view()),
    path("comments/<int:pk>/", CommentDetailView.as_view()),
    path("captcha/", CaptchaAPIView.as_view()),
    path("comments/<int:pk>/upload/", AttachmentUploadView.as_view()),
]
