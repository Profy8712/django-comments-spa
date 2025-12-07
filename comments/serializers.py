import re
import bleach
from captcha.models import CaptchaStore
from rest_framework import serializers

from .models import Comment, Attachment

# Only Latin letters and digits
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9]+$")

# Allowed HTML tags in text
ALLOWED_TAGS = ["a", "code", "i", "strong"]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for reading attachment info."""

    class Meta:
        model = Attachment
        fields = ["id", "file", "uploaded_at"]


class AttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for uploading an attachment."""

    class Meta:
        model = Attachment
        fields = ["id",        # returned
                  "file",      # uploaded file
                  "comment",   # comment ID
                  "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class CommentSerializer(serializers.ModelSerializer):
    """Main serializer for creating and displaying comments."""

    attachments = AttachmentSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    captcha_key = serializers.CharField(write_only=True, required=True)
    captcha_value = serializers.CharField(write_only=True, required=True)

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
            "captcha_value",
        ]
        read_only_fields = ["id", "created_at", "attachments", "children"]

    def validate_user_name(self, value):
        if not USERNAME_REGEX.match(value):
            raise serializers.ValidationError(
                "User name must contain only Latin letters and digits."
            )
        return value

    def validate_text(self, value):
        """Clean HTML and allow only specific tags."""
        return bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )

    def validate(self, attrs):
        """Validate CAPTCHA."""
        key = attrs.get("captcha_key")
        entered = attrs.get("captcha_value")

        queryset = CaptchaStore.objects.filter(
            hashkey=key,
            response__iexact=entered,
        )

        if not queryset.exists():
            raise serializers.ValidationError(
                {"captcha_value": "Invalid CAPTCHA value."}
            )

        # Delete captcha after successful check
        queryset.delete()

        return attrs

    def get_children(self, obj):
        children = obj.children.all().order_by("-created_at")
        return CommentSerializer(children, many=True, context=self.context).data
