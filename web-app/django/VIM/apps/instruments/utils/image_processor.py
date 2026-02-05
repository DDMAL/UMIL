"""Utility functions for processing instrument images."""

from PIL import Image


def calculate_compression_ratio(width: int, height: int) -> float:
    """
    Calculate compression ratio based on image dimensions.
    Extracted from download_imgs.py for reusability.

    Returns:
        0.2 for images > 4000px (20% of original)
        0.5 for images > 2000px (50% of original)
        0.75 for images > 1000px (75% of original)
        0.9 for images <= 1000px (90% of original)
    """
    max_dimension = max(width, height)

    if max_dimension > 4000:
        return 0.2
    elif max_dimension > 2000:
        return 0.5
    elif max_dimension > 1000:
        return 0.75
    else:
        return 0.9


def create_thumbnail_image(source_image: Image.Image) -> Image.Image:
    """
    Create a thumbnail from a PIL Image object.
    Core reusable logic for both file-based and upload-based workflows.

    Args:
        source_image: PIL Image object to resize

    Returns:
        Resized PIL Image object (new copy, original unchanged)

    Raises:
        IOError: If image processing fails
    """
    width, height = source_image.size
    compression_ratio = calculate_compression_ratio(width, height)
    new_size = (
        int(width * compression_ratio),
        int(height * compression_ratio),
    )

    # Important: thumbnail() modifies in-place, so work on a copy
    thumbnail = source_image.copy()
    thumbnail.thumbnail(new_size)
    return thumbnail


def process_uploaded_image(uploaded_file, umil_id: str) -> tuple:
    """
    Process uploaded image for Django FileField.save() usage.
    Creates ContentFile objects for both original and thumbnail versions.

    Args:
        uploaded_file: Django UploadedFile object from request.FILES
        umil_id: UMIL identifier (e.g., "UMIL-00001")

    Returns:
        tuple: (original_content, thumbnail_content, file_extension)
        - original_content: ContentFile ready for av_resource.file.save()
        - thumbnail_content: ContentFile ready for thumbnail_av.file.save()
        - file_extension: Original file extension (e.g., 'jpg', 'png')

    Raises:
        IOError: If image processing fails
        ValueError: If image format is unsupported
    """
    from django.core.files.base import ContentFile
    from io import BytesIO

    # Determine format from actual image format (not just content type)
    with Image.open(uploaded_file) as img:
        format_map = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}
        ext = format_map.get(img.format, "jpg")

    # Reset file pointer after reading
    uploaded_file.seek(0)

    # Read original content into memory
    original_content = ContentFile(uploaded_file.read(), name=f"{umil_id}.{ext}")

    # Generate thumbnail
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as img:
        thumbnail = create_thumbnail_image(img)

        # Convert thumbnail to PNG bytes
        thumb_buffer = BytesIO()
        thumbnail.save(thumb_buffer, "PNG")
        thumb_buffer.seek(0)
        thumbnail_content = ContentFile(thumb_buffer.read(), name=f"{umil_id}.png")

    return original_content, thumbnail_content, ext
