from django.urls import path

from .views import (
    MeAPIView,
    RegisterAPIView,
    TokenObtainPairAPIViewCustom,
    TokenRefreshAPIViewCustom,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairAPIViewCustom.as_view(), name="login"),
    path("refresh/", TokenRefreshAPIViewCustom.as_view(), name="token-refresh"),
    path("me/", MeAPIView.as_view(), name="me"),
]
