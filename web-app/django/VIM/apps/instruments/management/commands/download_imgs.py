import csv
import os
import requests
from PIL import Image
from io import BytesIO
from django.core.management.base import BaseCommand


class ImageDownloader:
    def __init__(self, user_agent, output_dir):
        self.headers = {"User-Agent": user_agent}
        self.original_img_dir = os.path.join(output_dir, "original")
        self.thumbnail_dir = os.path.join(output_dir, "thumbnail")
        os.makedirs(self.original_img_dir, exist_ok=True)
        os.makedirs(self.thumbnail_dir, exist_ok=True)

    def download_image_as_png(self, url, save_path):
        try:
            response = requests.get(url, stream=True, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            self._save_image_as_png(response.content, save_path)
            print(f"Downloaded {url} to {save_path}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
        except Exception as e:
            print(f"Error processing {url}: {e}")

    def _save_image_as_png(self, img_content, save_path):
        img = Image.open(BytesIO(img_content))
        img.save(save_path, "PNG")

    def create_thumbnail(self, image_path, thumbnail_path, compression_ratio=0.35):
        try:
            with Image.open(image_path) as original_img:
                new_size = (
                    int(original_img.width * compression_ratio),
                    int(original_img.height * compression_ratio),
                )
                original_img.thumbnail(new_size)
                original_img.save(thumbnail_path, "PNG")
                print(f"Created thumbnail for {image_path}")
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")

    def process_images(self, csv_file_path):
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

                if not os.path.exists(thumbnail_path):
                    self.create_thumbnail(save_path_png, thumbnail_path)


class Command(BaseCommand):
    help = "Download images and create thumbnails for instruments"

    def handle(self, *args, **options):
        user_agent = (
            "UMIL/0.1.0 (https://vim.simssa.ca/; https://ddmal.music.mcgill.ca/)"
        )
        output_dir = "VIM/apps/instruments/static/instruments/images/instrument_imgs"
        csv_file_path = "startup_data/vim_instruments_with_images-15sept.csv"

        downloader = ImageDownloader(user_agent, output_dir)
        downloader.process_images(csv_file_path)
        print("Images downloaded and thumbnails created")
