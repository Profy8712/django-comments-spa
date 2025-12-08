from captcha.models import CaptchaStore
from rest_framework import serializers

from .models import Comment, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "file", "created_at")


class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "comment", "file")
        read_only_fields = ("id",)


class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    # These fields are only used for validation, not stored in the model
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "user_name",
            "email",
            "homepage",
            "text",
            "parent",
            "created_at",
            "attachments",
            "captcha_key",
            "captcha_value",
        )
        read_only_fields = ("id", "created_at", "attachments")

    def validate(self, attrs):
        key = attrs.get("captcha_key")
        value = attrs.get("captcha_value")

        if not key or not value:
            raise serializers.ValidationError(
                {"captcha_value": ["CAPTCHA is required."]}
            )

        try:
            store = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError(
                {"captcha_value": ["Invalid CAPTCHA value."]}
            )

        # Case-insensitive comparison
        expected = (store.response or "").strip().lower()
        given = (value or "").strip().lower()

        if expected != given:
            raise serializers.ValidationError(
                {"captcha_value": ["Invalid CAPTCHA value."]}
            )

        # Remove used captcha entry so it cannot be reused
        store.delete()

        return attrs

    def create(self, validated_data):
        # Remove non-model fields before creating the Comment instance
        validated_data.pop("captcha_key", None)
        validated_data.pop("captcha_value", None)
        return super().create(validated_data)
