from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, MeSerializer, RegisterSerializer

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-issue tokens on register (common UX for SPA)
        refresh = RefreshToken.for_user(user)
        data = {
            "user": MeSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        data = {
            "user": MeSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    Optional: blacklist refresh token (works only if blacklist app is enabled).
    If blacklist is not enabled -> will return 200 but do nothing server-side.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh)
            # This requires SIMPLEJWT blacklist app. If not installed -> exception.
            token.blacklist()
        except Exception:
            # If blacklist isn't enabled, we still respond OK (client deletes tokens).
            pass

        return Response({"detail": "logged out"}, status=status.HTTP_200_OK)
