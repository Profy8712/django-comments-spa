# core/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from comments.views import CaptchaAPIView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Comments API (list, create, detail, upload)
    path(
        "api/comments/",
        include(("comments.urls", "comments"), namespace="comments"),
    ),

    # CAPTCHA JSON API for SPA
    path(
        "api/captcha/",
        CaptchaAPIView.as_view(),
        name="api_captcha",
    ),

    # Django Simple Captcha routes (image generation, forms, etc.)
    path("captcha/", include("captcha.urls")),
]

# Media files (attachments) when DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
