"""This module imports instrument objects from Wikidata for the VIM project."""

import csv
import glob
import os
from typing import Optional
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from VIM.apps.instruments.models import (
    Instrument,
    InstrumentName,
    Language,
    AVResource,
    HornbostelSachs,
)
from VIM.apps.instruments.utils.validators import validate_image_extension


class Command(BaseCommand):
    """
    The import_instruments command imports instrument objects from Wikidata.

    NOTE: For now, this script only imports instrument names in English and French. It
    also only imports a set of previously-curated instruments that have images available.
    This list of instruments is stored in startup_data/umil_instruments_15July_2025.csv
    """

    help = "Imports instrument objects"

    def __init__(self):
        super().__init__()
        self.language_map: dict[str, Language] = {}
        User = get_user_model()
        self.default_contributor = User.objects.get(username=settings.DDMAL_USERNAME)
        if not self.default_contributor:
            raise ValueError(
                f"Default contributor {settings.DDMAL_USERNAME} not found in the database."
            )

    def parse_instrument_data(
        self, instrument_id: str, instrument_data: dict
    ) -> dict[str, str | dict[str, str]]:
        """
        Given a dictionary response from the wbgetentities API, parse the data into a
        dictionary of desired instrument data.

        instrument_id [str]: Wikidata ID of the instrument
        instrument_data [dict]: Dictionary response from wbgetentities API

        return [dict]: Dictionary of parsed instrument data, containing the following
            keys:
            - wikidata_id [str]: Wikidata ID of the instrument
            - ins_names [dict]: Dictionary of instrument names, with language codes as
                keys and instrument names as values
            - hornbostel_sachs_class [str]: Hornbostel-Sachs classification of the
                instrument
            - mimo_class [str]: MIMO classification of the instrument
        """
        # Get available instrument names
        ins_labels: dict = instrument_data["labels"]
        ins_names: dict[str, str] = {
            value["language"]: value["value"] for key, value in ins_labels.items()
        }
        ins_aliases: dict = instrument_data["aliases"]
        ins_aliases_dict: dict[str, list[str]] = {
            key: [alias["value"] for alias in value]
            for key, value in ins_aliases.items()
        }
        # Get Hornbostel-Sachs and MIMO classifications, if available
        ins_hbs: Optional[list[dict]] = instrument_data["claims"].get("P1762")
        ins_mimo: Optional[list[dict]] = instrument_data["claims"].get("P3763")
        if ins_hbs and ins_hbs[0]["mainsnak"]["snaktype"] == "value":
            hbs_class: str = ins_hbs[0]["mainsnak"]["datavalue"]["value"]
        else:
            hbs_class = settings.EMPTY_HBS_CATEGORY
        if ins_mimo and ins_mimo[0]["mainsnak"]["snaktype"] == "value":
            mimo_class: str = ins_mimo[0]["mainsnak"]["datavalue"]["value"]
        else:
            mimo_class = ""
        parsed_data: dict[str, str | dict[str, str]] = {
            "wikidata_id": instrument_id,
            "ins_names": ins_names,
            "hornbostel_sachs_class": hbs_class,
            "mimo_class": mimo_class,
            "ins_aliases": ins_aliases_dict,
        }
        return parsed_data

    def get_instrument_data(self, instrument_ids: list[str]) -> list[dict]:
        """
        Given a list of Wikidata IDs, query the wbgetentities API and return a list of
        parsed instrument data.

        instrument_ids [list[str]]: List of Wikidata IDs of instruments

        return [list[dict]]: List of parsed instrument data. See parse_instrument_data
            for details.
        """
        ins_ids_str: str = "|".join(instrument_ids)
        url = (
            "https://www.wikidata.org/w/api.php?action=wbgetentities&"
            f"ids={ins_ids_str}&format=json&props=labels|descriptions|claims|aliases"
        )
        headers = {"User-Agent": "UMIL/0.1.0 (https://umil.linkedmusic.ca/)"}
        response = requests.get(url, timeout=10, headers=headers)
        response_entities = response.json()["entities"]
        instrument_data = [
            self.parse_instrument_data(key, value)
            for key, value in response_entities.items()
        ]
        return instrument_data

    def create_database_objects(
        self,
        instrument_attrs: dict,
        original_img_path: Optional[str],
        thumbnail_img_path: Optional[str],
    ) -> None:
        """
        Given a dictionary of instrument attributes and a url to an instrument image,
        create the corresponding database objects.

        instrument_attrs [dict]: Dictionary of instrument attributes. See
            parse_instrument_data for details.
        original_img_path [str]: Path to the original instrument image
        thumbnail_img_path [str]: Path to the thumbnail of the instrument image
        """
        ins_names = instrument_attrs.pop("ins_names")
        ins_aliases = instrument_attrs.pop("ins_aliases")

        # Create instrument using only the remaining valid fields
        # Generate UMIL ID for new instruments
        instrument, created = Instrument.objects.update_or_create(
            wikidata_id=instrument_attrs["wikidata_id"],
            defaults={
                "mimo_class": instrument_attrs["mimo_class"],
            },
        )

        # If newly created and no umil_id, generate one.
        # Wrap in its own atomic block so the select_for_update() lock inside
        # generate_umil_id() is scoped to this savepoint and released as soon
        # as the save completes, rather than being held for the entire outer
        # transaction (the full import loop).
        if created and not instrument.umil_id:
            with transaction.atomic():
                instrument.umil_id = Instrument.generate_umil_id()
                instrument.save(update_fields=["umil_id"])

        # Create or update instrument labels in the database (umil_label=True)
        for lang, name in ins_names.items():
            # Skip if the language code is not found in the database.
            # This commonly happens for codes like "mul" (multiple languages),
            # which are not intended to be used for individual instrument names.
            # See https://www.wikidata.org/wiki/Help:Default_values_for_labels_and_aliases
            if lang not in self.language_map:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping language {lang} for instrument {instrument.wikidata_id} as the language is not found in the database."
                    )
                )
                continue
            InstrumentName.objects.update_or_create(
                instrument=instrument,
                language=self.language_map[lang],
                umil_label=True,
                defaults={
                    "name": name,
                    "source_name": "Wikidata",
                    "contributor": self.default_contributor,
                    "verification_status": "verified",
                    "on_wikidata": True,
                },
            )

        # Create or update instrument aliases in the database (umil_label=False)
        for lang, aliases in ins_aliases.items():
            # Skip if the language code is not found in the database.
            if lang not in self.language_map:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping language {lang} for instrument {instrument.wikidata_id} as the language is not found in the database."
                    )
                )
                continue
            for alias in aliases:
                InstrumentName.objects.update_or_create(
                    instrument=instrument,
                    language=self.language_map[lang],
                    name=alias,
                    umil_label=False,
                    defaults={
                        "source_name": "Wikidata",
                        "contributor": self.default_contributor,
                        "verification_status": "verified",
                        "on_wikidata": True,
                    },
                )

        # Set Hornbostel-Sachs classification if present
        hbs_value = (
            instrument_attrs["hornbostel_sachs_class"] or settings.EMPTY_HBS_CATEGORY
        )
        hbs_obj = None
        if hbs_value and hbs_value != settings.EMPTY_HBS_CATEGORY:
            hbs_obj = HornbostelSachs.objects.create(
                instrument=instrument,
                hbs_class=hbs_value,
                is_main=True,
                review_status="verified",
                contributor=self.default_contributor,
            )
        instrument.hornbostel_sachs_class = hbs_obj

        # Create AVResource objects only when both image paths are available
        if original_img_path and thumbnail_img_path:
            # Validate extensions before creating AVResource objects
            try:
                original_format = validate_image_extension(original_img_path)
                thumbnail_format = validate_image_extension(thumbnail_img_path)
            except ValidationError as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Skipping images for {instrument.umil_id} (invalid format): {e}"
                    )
                )
                instrument.save()  # Save instrument even if images are skipped
                return

            img_obj, _ = AVResource.objects.update_or_create(
                instrument=instrument,
                url=original_img_path,
                defaults={
                    "type": "image",
                    "format": original_format,
                    "source_name": "Wikidata",
                },
            )
            instrument.default_image = img_obj
            thumbnail_obj, _ = AVResource.objects.update_or_create(
                instrument=instrument,
                url=thumbnail_img_path,
                defaults={
                    "type": "image",
                    "format": thumbnail_format,
                    "source_name": "Wikidata",
                },
            )
            instrument.thumbnail = thumbnail_obj

        instrument.save()

    @staticmethod
    def find_image_file(directory, ins_id):
        """Find an image file for the given instrument ID, regardless of extension.

        Returns the relative path (matching the directory format used for AVResource.url)
        or None if no file is found.
        """
        # directory is a relative path like "downloads/original"
        # The actual files are under MEDIA_ROOT
        abs_dir = os.path.join(settings.MEDIA_ROOT, directory)
        matches = glob.glob(os.path.join(abs_dir, f"{ins_id}.*"))
        if not matches:
            return None
        # Return relative path (for AVResource.url storage)
        filename = os.path.basename(
            matches[0]
        )  # each instrument is guaranteed to have at most one image
        return os.path.join(directory, filename)

    def handle(self, *args, **options) -> None:
        # Use smaller test dataset when in test mode
        csv_file = (
            "startup_data/test_instruments.csv"
            if os.getenv("MODE") == "test"
            else "startup_data/umil_instruments_15July_2025.csv"
        )

        with open(csv_file, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            instrument_list: list[dict] = list(reader)
        self.language_map = Language.objects.in_bulk(field_name="wikidata_code")
        img_dir = "downloads"
        with transaction.atomic():
            for ins_i in range(0, len(instrument_list), 50):
                ins_ids_subset: list[str] = [
                    ins["instrument"].split("/")[-1]
                    for ins in instrument_list[ins_i : ins_i + 50]
                ]
                ins_data: list[dict] = self.get_instrument_data(ins_ids_subset)
                for instrument_attrs, ins_id in zip(ins_data, ins_ids_subset):
                    original_img_path = self.find_image_file(
                        os.path.join(img_dir, "original"), ins_id
                    )
                    thumbnail_img_path = self.find_image_file(
                        os.path.join(img_dir, "thumbnail"), ins_id
                    )
                    if not original_img_path or not thumbnail_img_path:
                        self.stderr.write(
                            self.style.WARNING(
                                f"Missing image files for {ins_id}, creating instrument without images"
                            )
                        )
                    self.create_database_objects(
                        instrument_attrs, original_img_path, thumbnail_img_path
                    )
