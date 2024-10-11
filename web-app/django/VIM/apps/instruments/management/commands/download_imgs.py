"""This module downloads images from the web and creates thumbnails for the VIM instruments."""

import csv
import os
from io import BytesIO
import requests
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django management command to download images and create thumbnails for instruments."""

    USER_AGENT = "UMIL/0.1.0 (https://vim.simssa.ca/; https://ddmal.music.mcgill.ca/)"
    OUTPUT_DIR = os.path.join(
        settings.STATIC_ROOT, "instruments", "images", "instrument_imgs"
    )
    CSV_PATH = "startup_data/all_instruments_11oct_2024.csv"

    help = "Download images and create thumbnails for instruments"

    def __init__(self):
        super().__init__()
        self.headers = {"User-Agent": self.USER_AGENT}
        self.original_img_dir = os.path.join(self.OUTPUT_DIR, "original")
        self.thumbnail_dir = os.path.join(self.OUTPUT_DIR, "thumbnail")
        os.makedirs(self.original_img_dir, exist_ok=True)
        os.makedirs(self.thumbnail_dir, exist_ok=True)

    def download_image_as_png(self, url, save_path):
        """Download an image from a URL and save it as a PNG file."""
        try:
            response = requests.get(url, stream=True, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            self._save_image_as_png(response.content, url, save_path)
        except requests.RequestException as e:
            self.stderr.write(f"Failed to download image from {url}: {e}")

    def _save_image_as_png(self, img_content, url, save_path):
        """Save image content as a PNG file."""
        try:
            img = Image.open(BytesIO(img_content))
            img.save(save_path, "PNG")
            self.stdout.write(f"Saved image at {save_path}")
        except IOError as e:
            self.stderr.write(f"Failed to save image from {url}: {e}")

    def calculate_compression_ratio(self, original_width, original_height):
        """
        Calculate a flexible compression ratio based on the original dimensions of an image.

        Parameters:
        original_width (int): The width of the original image.
        original_height (int): The height of the original image.

        Returns:
        float: The compression ratio.
        """
        # Determine the larger dimension to base compression on (could be width or height)
        max_dimension = max(original_width, original_height)

        # Set a target size for compression based on original dimensions
        if max_dimension > 4000:
            # Large images (e.g., 4K or higher): compress significantly
            compression_ratio = 0.2  # 20% of the original size
        elif max_dimension > 2000:
            # Medium-large images: moderate compression
            compression_ratio = 0.5  # 50% of the original size
        elif max_dimension > 1000:
            # Medium images: light compression
            compression_ratio = 0.75  # 75% of the original size
        else:
            # Small images: minimal compression
            compression_ratio = 0.9  # 90% of the original size

        return compression_ratio

    def create_thumbnail(self, image_path, thumbnail_path):
        """Create a thumbnail of an image."""
        try:
            with Image.open(image_path) as original_img:
                original_width, original_height = original_img.size
                compression_ratio = self.calculate_compression_ratio(
                    original_width, original_height
                )
                new_size = (
                    int(original_width * compression_ratio),
                    int(original_height * compression_ratio),
                )
                original_img.thumbnail(new_size)
                original_img.save(thumbnail_path, "PNG")
            self.stdout.write(f"Created thumbnail at {thumbnail_path}")
        except IOError as e:
            self.stderr.write(f"Failed to create thumbnail for {image_path}: {e}")

    def process_images(self, csv_file_path):
        """Process images from a CSV file."""
        with open(csv_file_path, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                image_url = row["image"]
                instrument_wikidata_id = row["instrument"].split("/")[-1]
                save_path_png = os.path.join(
                    self.original_img_dir, f"{instrument_wikidata_id}.png"
                )
                thumbnail_path = os.path.join(
                    self.thumbnail_dir, f"{instrument_wikidata_id}.png"
                )

                if not os.path.exists(save_path_png):
                    self.download_image_as_png(image_url, save_path_png)

                if not os.path.exists(thumbnail_path) and os.path.exists(save_path_png):
                    self.create_thumbnail(save_path_png, thumbnail_path)

    def handle(self, *args, **options):
        """Handle the command."""
        self.process_images(self.CSV_PATH)
        self.stdout.write("Images downloaded and thumbnails created")
