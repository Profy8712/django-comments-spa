import os

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image


class Comment(models.Model):
    user_name = models.CharField(max_length=50)
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True)
    text = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # LIFO по умолчанию

    def __str__(self) -> str:
        return f"{self.user_name}: {self.text[:30]}"


def attachment_upload_to(instance: "Attachment", filename: str) -> str:
    """
    Upload path for attachments.

    Files will be stored under:
    media/attachments/<comment_id>/<filename>
    """
    return f"attachments/{instance.comment_id}/{filename}"


class Attachment(models.Model):
    """
    Attachment model for images and text files.

    Requirements:
    - Image formats: JPG, JPEG, PNG, GIF.
    - Text file format: TXT, size <= 100 KB.
    - Images larger than 320x240 are proportionally resized down.
    """

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        upload_to=attachment_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "gif", "txt"]
            )
        ],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    MAX_TEXT_SIZE_BYTES = 100 * 1024  # 100 KB
    MAX_IMAGE_WIDTH = 320
    MAX_IMAGE_HEIGHT = 240

    def clean(self):
        """
        Validate text file size.
        """
        super().clean()

        if not self.file:
            return

        ext = os.path.splitext(self.file.name)[1].lower()

        if ext == ".txt" and self.file.size > self.MAX_TEXT_SIZE_BYTES:
            raise ValidationError("Text file size must be <= 100 KB.")

    def save(self, *args, **kwargs):
        """
        Resize image files if they exceed max dimensions.
        """
        super().save(*args, **kwargs)

        if not self.file:
            return

        ext = os.path.splitext(self.file.name)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".gif"}:
            return

        file_path = self.file.path

        try:
            img = Image.open(file_path)
        except OSError:
            # Not an image or corrupted file – just skip resizing
            return

        width, height = img.size
        max_w, max_h = self.MAX_IMAGE_WIDTH, self.MAX_IMAGE_HEIGHT

        # No need to resize
        if width <= max_w and height <= max_h:
            return

        img.thumbnail((max_w, max_h))
        # сохраняем в исходном формате, если возможно
        img.save(file_path, format=img.format or "PNG")
