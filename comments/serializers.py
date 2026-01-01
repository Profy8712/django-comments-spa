import os
import re
from typing import Optional

from captcha.models import CaptchaStore
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from .models import Attachment, Comment


class AttachmentSerializer(serializers.ModelSerializer):
    # Keep field name "file" for frontend compatibility
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ("id", "file", "uploaded_at")

    def get_file(self, obj) -> Optional[str]:
        """
        Return relative URL like "/media/attachments/...".
        Works locally (Vite proxy) and in production (nginx serves /media).
        """
        if not obj.file:
            return None
        try:
            return obj.file.url
        except Exception:
            return None


class AttachmentUploadSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ("id", "file", "upload_key", "uploaded_at")

    def get_file(self, obj) -> Optional[str]:
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
        qs = obj.children.all().order_by("created_at")
        return CommentChildSerializer(qs, many=True, context=self.context).data


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

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
            attrs["user_name"] = getattr(user, "username", "") or attrs.get("user_name") or ""
            attrs["email"] = getattr(user, "email", "") or attrs.get("email") or ""
            attrs.pop("captcha_key", None)
            attrs.pop("captcha_value", None)
            return attrs

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


class CommentCreateSerializer(CommentSerializer):
    """
    Create comment and optionally attach files.

    Supports two workflows:
    1) Two-step upload (JWT):
       - POST /api/comments/upload/ (multipart, returns {id, upload_key})
       - POST /api/comments/ with {attachment_ids: [...], upload_key: "..."} to bind
       This needs MOVING files from tmp to comment folder (fixed below).

    2) Single-step create with files:
       - POST /api/comments/ as multipart with files[] + fields (optional)
       Will create Attachment(comment=comment, file=f) directly.
    """

    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    upload_key = serializers.UUIDField(required=False, write_only=True)

    # Optional single-request upload
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ("attachment_ids", "upload_key", "files")

    def validate(self, attrs):
        attrs = super().validate(attrs)

        ids = attrs.get("attachment_ids") or []
        key = attrs.get("upload_key")

        if ids and not key:
            raise serializers.ValidationError(
                {"upload_key": ["upload_key is required when attachment_ids provided"]}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ids = validated_data.pop("attachment_ids", [])
        key = validated_data.pop("upload_key", None)
        files = validated_data.pop("files", [])

        comment = super().create(validated_data)

        # Single-step: create attachments already bound to comment
        for f in files:
            Attachment.objects.create(comment=comment, file=f)

        # Two-step: bind temp attachments (comment is NULL) and MOVE files to comment folder
        if ids:
            attachments = list(
                Attachment.objects.select_for_update().filter(
                    id__in=ids,
                    upload_key=key,
                    comment__isnull=True,
                )
            )
            if len(attachments) != len(ids):
                raise serializers.ValidationError(
                    {"attachment_ids": ["Some attachments are invalid or already used"]}
                )

            for att in attachments:
                # bind
                att.comment = comment

                # move file by re-saving it (upload_to will now resolve to attachments/<comment_id>/...)
                old_name = att.file.name
                data = att.file.read()
                filename = os.path.basename(old_name)

                att.file.save(filename, ContentFile(data), save=False)
                att.save()

        return comment


class CommentSearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_name = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)
    text = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(allow_null=True, required=False)
