from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    RegisterResponseSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)

User = get_user_model()


class RegisterAPIView(APIView):
    """
    POST /api/accounts/register/
    Create a new user and return user + JWT tokens.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # avoid CSRF/session noise for pure JSON endpoint

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterResponseSerializer},
        tags=["accounts"],
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        payload = {
            "user": UserPublicSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(payload, status=status.HTTP_201_CREATED)


class MeAPIView(APIView):
    """
    GET /api/accounts/me/
    Return current authenticated user info including admin flags.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserPublicSerializer},
        tags=["accounts"],
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        data = UserPublicSerializer(user).data

        # Ensure frontend can detect admin
        data["is_staff"] = bool(user.is_staff)
        data["is_superuser"] = bool(user.is_superuser)

        return Response(data, status=status.HTTP_200_OK)


class TokenObtainPairAPIViewCustom(TokenObtainPairView):
    """
    Optional custom JWT obtain endpoint (if you use it in accounts app).
    """
    permission_classes = [permissions.AllowAny]


class TokenRefreshAPIViewCustom(TokenRefreshView):
    """
    Optional custom JWT refresh endpoint (if you use it in accounts app).
    """
    permission_classes = [permissions.AllowAny]
