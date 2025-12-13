from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from comments.views import CaptchaAPIView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Comments REST API
    path(
        "api/comments/",
        include(("comments.urls", "comments"), namespace="comments"),
    ),

    # CAPTCHA JSON API for SPA
    path("api/captcha/", CaptchaAPIView.as_view(), name="api_captcha"),

    # Django Simple Captcha built-in routes
    path("captcha/", include("captcha.urls")),
]

# Serve media in dev only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
