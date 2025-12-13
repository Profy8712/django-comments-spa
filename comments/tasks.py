from __future__ import annotations

from pathlib import Path

from celery import shared_task
from django.conf import settings

from PIL import Image

from .models import Attachment


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def resize_attachment_image(self, attachment_id: int, max_width: int = 320, max_height: int = 240) -> None:
    attachment = Attachment.objects.filter(id=attachment_id).first()
    if not attachment or not attachment.file:
        return

    file_path = Path(settings.MEDIA_ROOT) / attachment.file.name
    if not file_path.exists():
        return

    try:
        with Image.open(file_path) as img:
            img_format = (img.format or "").upper()

            # Only handle supported image formats
            if img_format not in {"JPEG", "JPG", "PNG", "GIF"}:
                return

            # Pillow uses "JPEG" format string
            if img_format == "JPG":
                img_format = "JPEG"

            # Resize proportionally (in-place)
            img.thumbnail((max_width, max_height))

            save_kwargs = {}
            if img_format == "JPEG":
                save_kwargs["quality"] = 85
                save_kwargs["optimize"] = True

            img.save(file_path, format=img_format, **save_kwargs)

    except Exception as exc:
        raise self.retry(exc=exc)
