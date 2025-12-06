import re

import bleach
from captcha.models import CaptchaStore
from rest_framework import serializers

from .models import Comment, Attachment

# Username: only Latin letters and digits
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9]+$")

# Allowed HTML tags and attributes
ALLOWED_TAGS = ["a", "code", "i", "strong"]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for file attachments."""

    class Meta:
        model = Attachment
        fields = ["id", "file", "uploaded_at"]


class AttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a single attachment."""

    class Meta:
        model = Attachment
        fields = ["id", "file", "comment", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class CommentSerializer(serializers.ModelSerializer):
    """Main serializer for Comment model with validation and HTML cleaning."""

    attachments = AttachmentSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    # CAPTCHA fields (write-only)
    captcha_key = serializers.CharField(write_only=True, required=True)
    captcha_text = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user_name",
            "email",
            "homepage",
            "text",
            "parent",
            "created_at",
            "attachments",
            "children",
            "captcha_key",
            "captcha_text",
        ]
        read_only_fields = ["id", "created_at", "attachments", "children"]

    def validate_user_name(self, value: str) -> str:
        """Validate username for Latin letters and digits."""
        if not USERNAME_REGEX.match(value):
            raise serializers.ValidationError(
                "User name must contain only Latin letters and digits."
            )
        return value

    def validate_text(self, value: str) -> str:
        """Clean HTML and allow only specific tags."""
        cleaned = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )
        return cleaned

    def validate(self, attrs):
        """Validate CAPTCHA using django-simple-captcha."""
        captcha_key = attrs.pop("captcha_key", None)
        captcha_text = attrs.pop("captcha_text", None)

        if not captcha_key or not captcha_text:
            raise serializers.ValidationError(
                {"captcha_text": "CAPTCHA is required."}
            )

        qs = CaptchaStore.objects.filter(
            hashkey=captcha_key,
            response__iexact=captcha_text,
        )

        if not qs.exists():
            raise serializers.ValidationError(
                {"captcha_text": "Invalid CAPTCHA value."}
            )

        # Invalidate used CAPTCHA
        qs.delete()

        return attrs

    def get_children(self, obj):
        """Return nested child comments (recursive)."""
        children_qs = obj.children.all().order_by("-created_at")
        return CommentSerializer(children_qs, many=True, context=self.context).data
