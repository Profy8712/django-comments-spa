from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def api_root(request):
    """
    Lightweight API root for debugging / discoverability.
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

    # JWT
    path("api/auth/token/", TokenObtainPairView.as_view(), name="jwt-token-obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="jwt-token-refresh"),

    # Apps API
    path("api/comments/", include("comments.urls")),
    path("api/accounts/", include("accounts.urls")),

    # CAPTCHA (django-simple-captcha)
    path("captcha/", include("captcha.urls")),
]

# Media (local/dev only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
