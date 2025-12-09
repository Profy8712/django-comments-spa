from captcha.models import CaptchaStore
from rest_framework import serializers

from .models import Comment, Attachment


class RecursiveField(serializers.Serializer):
    """
    Recursive field used to serialize nested children comments.
    It reuses the parent serializer class for the child instances.
    """

    def to_representation(self, value):
        serializer_class = self.parent.parent.__class__
        serializer = serializer_class(value, context=self.context)
        return serializer.data


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        # IMPORTANT: the model field is `uploaded_at`, not `created_at`
        fields = ("id", "file", "uploaded_at")


class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "comment", "file")
        read_only_fields = ("id",)


class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    children = RecursiveField(many=True, read_only=True)

    # These fields are used only for CAPTCHA validation,
    # they are not stored in the model.
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
            "children",
            "captcha_key",
            "captcha_value",
        )
        read_only_fields = ("id", "created_at", "attachments", "children")

    def validate(self, attrs):
        """
        Validate CAPTCHA: key must exist and value must match
        (case-insensitive). Used entries are deleted.
        """
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

        expected = (store.response or "").strip().lower()
        given = (value or "").strip().lower()

        if expected != given:
            raise serializers.ValidationError(
                {"captcha_value": ["Invalid CAPTCHA value."]}
            )

        # remove used CAPTCHA entry
        store.delete()
        return attrs

    def create(self, validated_data):
        """
        Remove non-model fields before creating a Comment instance.
        """
        validated_data.pop("captcha_key", None)
        validated_data.pop("captcha_value", None)
        return super().create(validated_data)
