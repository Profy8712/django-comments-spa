from django.urls import path

from .views import (
    MeAPIView,
    RegisterAPIView,
    TokenObtainPairAPIViewCustom,
    TokenRefreshAPIViewCustom,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("me/", MeAPIView.as_view(), name="me"),
    # Optional JWT endpoints (enable only if you actually route them)
    path("token/", TokenObtainPairAPIViewCustom.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshAPIViewCustom.as_view(), name="token_refresh"),
]
