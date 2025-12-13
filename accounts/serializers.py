from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def validate_username(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError(_("Username is required."))
        return value

    def validate_email(self, value: str) -> str:
        value = (value or "").strip()
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("User with this email already exists."))
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = (attrs.get("username") or "").strip()
        password = attrs.get("password") or ""

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(_("Invalid credentials."))

        attrs["user"] = user
        return attrs


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff", "is_superuser", "date_joined")
        read_only_fields = fields
