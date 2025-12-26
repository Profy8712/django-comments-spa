import re

from captcha.models import CaptchaStore
from rest_framework import serializers

from .models import Attachment, Comment


class AttachmentSerializer(serializers.ModelSerializer):
    # IMPORTANT: keep field name "file" for frontend compatibility
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ("id", "file", "uploaded_at")

    def get_file(self, obj) -> str | None:
        """
        Return RELATIVE URL like "/media/attachments/...".
        Works locally (Vite proxy) and in production (nginx serves /media).
        """
        if not obj.file:
            return None
        try:
            return obj.file.url
        except Exception:
            return None


class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "comment", "file")
        read_only_fields = ("id",)


# --- Recursive serializer for children (replies) ---
class CommentChildSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

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
        )

    def get_children(self, obj):
        # Replies should be shown UNDER parent (old -> new)
        qs = obj.children.all().order_by("created_at")
        return CommentChildSerializer(qs, many=True, context=self.context).data


class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    # CAPTCHA required ONLY for anonymous users
    captcha_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    captcha_value = serializers.CharField(write_only=True, required=False, allow_blank=True)

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

    def get_children(self, obj):
        # Replies should be shown UNDER parent (old -> new)
        qs = obj.children.all().order_by("created_at")
        return CommentChildSerializer(qs, many=True, context=self.context).data

    def validate_text(self, value: str) -> str:
        if value is None:
            return value

        text = str(value)

        # Block raw HTML
        if "<" in text or ">" in text:
            raise serializers.ValidationError(
                "Raw HTML is not allowed. Use pseudo-tags like [i]...[/i] instead."
            )

        allowed_tags = {"i", "strong", "code", "a"}
        tag_pattern = re.compile(r"\[(\/?)([a-zA-Z]+)(?:[^\]]*)]")

        stack: list[str] = []

        for match in tag_pattern.finditer(text):
            is_closing = bool(match.group(1))
            tag_name = match.group(2).lower()

            if tag_name not in allowed_tags:
                raise serializers.ValidationError(f"Tag [{tag_name}] is not allowed.")

            if not is_closing:
                stack.append(tag_name)
            else:
                if not stack or stack[-1] != tag_name:
                    raise serializers.ValidationError(
                        "Pseudo-tags are not balanced or properly nested."
                    )
                stack.pop()

        if stack:
            raise serializers.ValidationError(
                "Pseudo-tags are not balanced or properly nested."
            )

        return text

    def validate(self, attrs):
        """
        - Anonymous -> CAPTCHA required
        - Authenticated (JWT) -> CAPTCHA not required
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        is_auth = bool(user and user.is_authenticated)

        if is_auth:
            attrs.pop("captcha_key", None)
            attrs.pop("captcha_value", None)
            return attrs

        # anonymous: captcha required
        key = (attrs.get("captcha_key") or "").strip()
        value = (attrs.get("captcha_value") or "").strip()

        if not key or not value:
            raise serializers.ValidationError({"captcha_value": ["CAPTCHA is required."]})

        try:
            store = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({"captcha_value": ["Invalid CAPTCHA value."]})

        expected = (store.response or "").strip().lower()
        given = value.lower()

        if expected != given:
            raise serializers.ValidationError({"captcha_value": ["Invalid CAPTCHA value."]})

        store.delete()
        return attrs

    def create(self, validated_data):
        validated_data.pop("captcha_key", None)
        validated_data.pop("captcha_value", None)
        return super().create(validated_data)


class CommentSearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_name = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)
    text = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(allow_null=True, required=False)
