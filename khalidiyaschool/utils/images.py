from __future__ import annotations

import io
import os

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile

MAX_DIMENSION = 1200
WEBP_QUALITY = 85


def convert_image_to_webp(
    field: FieldFile,
    upload_path: str,
    max_dimension: int = MAX_DIMENSION,
    quality: int = WEBP_QUALITY,
) -> FieldFile:
    from PIL import Image  # deferred: safe to import before Pillow is installed at migration time

    if not field:
        return field

    field.seek(0)
    img = Image.open(field)
    img.load()

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    if max_dimension > 0:
        w, h = img.size
        longest = max(w, h)
        if longest > max_dimension:
            scale = max_dimension / longest
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buffer = io.BytesIO()
    save_kwargs: dict = {"format": "WEBP", "quality": quality}
    if img.mode == "RGBA":
        save_kwargs["lossless"] = False

    img.save(buffer, **save_kwargs)
    buffer.seek(0)

    original_name = os.path.basename(field.name or "image")
    stem = os.path.splitext(original_name)[0]
    new_name = f"{stem}.webp"

    field.save(new_name, ContentFile(buffer.read()), save=False)

    return field
