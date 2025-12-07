from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from comments.views import CaptchaAPIView

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API: Comments (list, create, detail, upload attachments)
    path("api/comments/", include("comments.urls")),

    # API: CAPTCHA for SPA
    path("api/captcha/", CaptchaAPIView.as_view(), name="api_captcha"),

    # Required for Django Simple Captcha admin & generation
    path("captcha/", include("captcha.urls")),
]

# Media files (attachments) when DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
