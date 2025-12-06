from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from comments.views import CaptchaAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/comments/", include("comments.urls")),
    path("api/captcha/", CaptchaAPIView.as_view(), name="api_captcha"),
    path("captcha/", include("captcha.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
