"""
Single source of truth for image format constants.

All format-related mappings are derived from STORABLE_FORMATS below.
To add a new format, add an entry there — all consumers pick it up automatically.

Download-specific constants (CONVERT_FORMATS, SKIP_FORMATS, DOWNLOAD_CONTENT_TYPE_MAP)
are also defined here since they reference the same format domain.
"""

# ── Core registry ──
# (extension, PIL_format_name_or_None, mime_type, human_label)
STORABLE_FORMATS = [
    ("jpg", "JPEG", "image/jpeg", "JPEG"),
    ("png", "PNG", "image/png", "PNG"),
    ("gif", "GIF", "image/gif", "GIF"),
    ("webp", "WEBP", "image/webp", "WebP"),
    ("svg", None, "image/svg+xml", "SVG (Scalable Vector Graphics)"),
]

# ── Download-only formats (recognized but not stored as-is) ──

# Formats converted to jpg/png during download
CONVERT_FORMATS = {"tiff", "tif", "bmp"}

# Formats rejected during download
SKIP_FORMATS = {"xcf"}

# MIME types for download-only formats
DOWNLOAD_CONTENT_TYPE_MAP = {
    "image/tiff": "tiff",
    "image/bmp": "bmp",
    "image/x-xcf": "xcf",
}

# ── Derived from STORABLE_FORMATS ──

# MIME type → extension mapping for format detection during download.
# Includes storable formats and download-only formats:
# {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif",
#  "image/webp": "webp", "image/svg+xml": "svg",
#  "image/tiff": "tiff", "image/bmp": "bmp", "image/x-xcf": "xcf"}
CONTENT_TYPE_MAP = {mime: ext for ext, _, mime, _ in STORABLE_FORMATS}
CONTENT_TYPE_MAP.update(DOWNLOAD_CONTENT_TYPE_MAP)

# Extensions preserved as-is during download (no conversion needed).
# {"jpg", "png", "gif", "webp", "svg", "jpeg"}
PRESERVE_FORMATS = {ext for ext, _, _, _ in STORABLE_FORMATS} | {"jpeg"}

# Extension → PIL format name for saving images and thumbnails.
# {"jpg": "JPEG", "png": "PNG", "gif": "GIF", "webp": "WEBP", "jpeg": "JPEG"}
# Note: SVG is excluded (PIL cannot process SVG files).
EXT_TO_PIL_FORMAT = {ext: pil for ext, pil, _, _ in STORABLE_FORMATS if pil}
EXT_TO_PIL_FORMAT["jpeg"] = "JPEG"

# PIL format name → (PIL save format, file extension) for upload processing.
# {"JPEG": ("JPEG", "jpg"), "PNG": ("PNG", "png"),
#  "GIF": ("GIF", "gif"), "WEBP": ("WEBP", "webp")}
# Note: SVG is excluded (user uploads don't support SVG).
PIL_FORMAT_TO_EXTENSION = {
    pil: (pil, ext) for ext, pil, _, _ in STORABLE_FORMATS if pil
}

# Django model choices for AVResource.format field.
# [("jpg", "JPEG"), ("jpeg", "JPEG (alternative extension)"),
#  ("png", "PNG"), ("gif", "GIF"), ("webp", "WebP"),
#  ("svg", "SVG (Scalable Vector Graphics)")]
IMAGE_FORMAT_CHOICES = [(ext, label) for ext, _, _, label in STORABLE_FORMATS]
IMAGE_FORMAT_CHOICES.insert(1, ("jpeg", "JPEG (alternative extension)"))

# Allowed file extensions for import/download validation.
# {"jpg", "jpeg", "png", "gif", "webp", "svg"}
ALLOWED_IMAGE_EXTENSIONS = {ext for ext, _, _, _ in STORABLE_FORMATS} | {"jpeg"}

# Allowed MIME types for user uploads.
# ["image/jpeg", "image/png", "image/gif", "image/webp"]
# Note: SVG is excluded for security (script injection risk).
ALLOWED_IMAGE_TYPES = [mime for ext, _, mime, _ in STORABLE_FORMATS if ext != "svg"]
