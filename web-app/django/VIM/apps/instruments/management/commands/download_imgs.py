"""This module downloads images from the web and creates thumbnails for the VIM instruments."""

import csv
import glob
import os
import shutil
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from VIM.apps.instruments.constants import (
    CONTENT_TYPE_MAP,
    CONVERT_FORMATS,
    EXT_TO_PIL_FORMAT,
    PRESERVE_FORMATS,
    SKIP_FORMATS,
)
from VIM.apps.instruments.utils.image_processor import create_thumbnail_image
from VIM.apps.instruments.utils.validators import validate_image_extension


class Command(BaseCommand):
    """Django management command to download images and create thumbnails for instruments."""

    USER_AGENT = "UMIL/0.1.0 (https://vim.simssa.ca/; https://ddmal.music.mcgill.ca/)"
    OUTPUT_DIR = os.path.join(
        settings.STATIC_ROOT, "instruments", "images", "instrument_imgs"
    )
    CSV_PATH = "startup_data/umil_instruments_15July_2025.csv"

    help = "Download images and create thumbnails for instruments"

    def __init__(self):
        super().__init__()
        self.headers = {"User-Agent": self.USER_AGENT}
        self.original_img_dir = os.path.join(self.OUTPUT_DIR, "original")
        self.thumbnail_dir = os.path.join(self.OUTPUT_DIR, "thumbnail")
        os.makedirs(self.original_img_dir, exist_ok=True)
        os.makedirs(self.thumbnail_dir, exist_ok=True)

    def detect_format(self, response, url):
        """Detect image format from Content-Type header, falling back to URL extension."""
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        ext = CONTENT_TYPE_MAP.get(content_type)
        if ext:
            return ext

        # Fall back to URL file extension
        path = urlparse(url).path
        url_ext = os.path.splitext(path)[1].lstrip(".").lower()
        if url_ext in PRESERVE_FORMATS | CONVERT_FORMATS | SKIP_FORMATS:
            return url_ext

        return None

    def download_image(self, url, ins_id):
        """Download an image, preserving its original format when possible.

        Returns the file extension used, or None if the download was skipped/failed.
        """
        try:
            response = requests.get(url, stream=True, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stderr.write(f"Failed to download image from {url}: {e}")
            return None

        fmt = self.detect_format(response, url)
        if fmt is None:
            self.stderr.write(f"Unknown image format for {url}, skipping")
            return None

        if fmt in SKIP_FORMATS:
            self.stderr.write(f"Skipping unsupported format '{fmt}' for {url}")
            return None

        content = response.content

        if fmt == "svg":
            save_path = os.path.join(self.original_img_dir, f"{ins_id}.svg")
            with open(save_path, "wb") as f:
                f.write(content)
            self.stdout.write(f"Saved SVG image at {save_path}")
            return "svg"

        if fmt in PRESERVE_FORMATS:
            ext = fmt if fmt != "jpeg" else "jpg"
            save_path = os.path.join(self.original_img_dir, f"{ins_id}.{ext}")
            with open(save_path, "wb") as f:
                f.write(content)
            self.stdout.write(f"Saved image at {save_path}")
            return ext

        # CONVERT_FORMATS (tiff, bmp): convert via PIL
        try:
            img = Image.open(BytesIO(content))
            has_transparency = img.mode in ("RGBA", "LA", "PA") or (
                img.mode == "P" and "transparency" in img.info
            )
            if has_transparency:
                ext = "png"
                save_path = os.path.join(self.original_img_dir, f"{ins_id}.png")
                img.save(save_path, "PNG")
            else:
                ext = "jpg"
                save_path = os.path.join(self.original_img_dir, f"{ins_id}.jpg")
                img.convert("RGB").save(save_path, "JPEG", quality=90)
            self.stdout.write(f"Converted {fmt} to {ext} at {save_path}")
            return ext
        except IOError as e:
            self.stderr.write(f"Failed to convert image from {url}: {e}")
            return None

    def create_thumbnail(self, image_path, ext):
        """Create a thumbnail preserving the original format.

        For SVG files, the original is copied as the thumbnail since SVG scales natively.
        """
        ins_filename = os.path.basename(image_path)
        thumbnail_path = os.path.join(self.thumbnail_dir, ins_filename)

        if ext == "svg":
            # SVG scales natively; copy as thumbnail
            shutil.copy2(image_path, thumbnail_path)
            self.stdout.write(f"Copied SVG as thumbnail at {thumbnail_path}")
            return

        try:
            with Image.open(image_path) as original_img:
                thumbnail = create_thumbnail_image(original_img)
                pil_format = EXT_TO_PIL_FORMAT.get(ext, "PNG")
                save_kwargs = {}
                if pil_format == "JPEG":
                    save_kwargs["quality"] = 90
                thumbnail.save(thumbnail_path, pil_format, **save_kwargs)
            self.stdout.write(f"Created thumbnail at {thumbnail_path}")
        except IOError as e:
            self.stderr.write(f"Failed to create thumbnail for {image_path}: {e}")

    def find_existing_image(self, directory, ins_id):
        """Find an existing image file for the given instrument ID, regardless of extension."""
        matches = glob.glob(os.path.join(directory, f"{ins_id}.*"))
        valid_exts = PRESERVE_FORMATS | CONVERT_FORMATS
        return next(
            (m for m in matches if os.path.splitext(m)[1].lstrip(".") in valid_exts),
            None,
        )

    def process_images(self, csv_file_path):
        """Process images from a CSV file."""
        with open(csv_file_path, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                image_url = row["image"]
                ins_id = row["instrument"].split("/")[-1]

                existing = self.find_existing_image(self.original_img_dir, ins_id)
                if existing:
                    # Validate extension of existing file
                    try:
                        ext = validate_image_extension(existing)
                    except ValidationError as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"Skipping {ins_id} (invalid existing file): {e}"
                            )
                        )
                        continue
                else:
                    ext = self.download_image(image_url, ins_id)

                if ext is None:
                    continue

                original_path = os.path.join(self.original_img_dir, f"{ins_id}.{ext}")
                existing_thumb = self.find_existing_image(self.thumbnail_dir, ins_id)
                if not existing_thumb and os.path.exists(original_path):
                    self.create_thumbnail(original_path, ext)

    def handle(self, *args, **options):
        """Handle the command."""
        self.process_images(self.CSV_PATH)
        self.stdout.write("Images downloaded and thumbnails created")
