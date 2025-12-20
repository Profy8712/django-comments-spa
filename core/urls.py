from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def api_root(request):
    """
    Optional API root for debugging / discoverability.
    Safe for local and production.
    """
    return JsonResponse(
        {
            "comments": "/api/comments/",
            "captcha": "/api/comments/captcha/",
            "auth_token": "/api/auth/token/",
            "auth_refresh": "/api/auth/token/refresh/",
            "accounts": "/api/accounts/",
            "admin": "/admin/",
        }
    )


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API root
    path("api/", api_root, name="api-root"),

    # JWT authentication
    path("api/auth/token/", TokenObtainPairView.as_view(), name="jwt-token-obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="jwt-token-refresh"),

    # Applications
    path("api/comments/", include("comments.urls")),
    path("api/accounts/", include("accounts.urls")),

    # django-simple-captcha (image, audio, reload)
    path("captcha/", include("captcha.urls")),
]

# Media (local / debug only)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
