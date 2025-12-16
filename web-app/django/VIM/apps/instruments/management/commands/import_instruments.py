"""This module imports instrument objects from Wikidata for the VIM project."""

import csv
import os
from typing import Optional
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource

HEADERS = {
    "User-Agent": "UMIL/0.1.0 (https://vim.simssa.ca/; https://ddmal.music.mcgill.ca/)"
}


class Command(BaseCommand):
    """
    The import_instruments command imports instrument objects from Wikidata.

    NOTE: For now, this script only imports instrument names in English and French. It
    also only imports a set of previously-curated instruments that have images available.
    This list of instruments is stored in startup_data/umil_instruments_15July_2025.csv
    """

    help = "Imports instrument objects"

    WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

    def __init__(self):
        super().__init__()
        self.language_map: dict[str, Language] = {}
        User = get_user_model()
        self.default_contributor = User.objects.get(username=settings.DDMAL_USERNAME)
        if not self.default_contributor:
            raise ValueError(
                f"Default contributor {settings.DDMAL_USERNAME} not found in the database."
            )

    def get_all_wikidata_images(
        self, instrument_qids: list[str], exclude_image_urls: list[str]
    ) -> dict[str, list[str]]:
        """
        For the given list of instrument Wikidata QIDs, fetch all image URLs (P18) except
        those specified in exclude_image_urls, which could be empty.
        Returns a dict: {qid: [image_url, ...], ...}
        """
        if not instrument_qids:
            return {}

        # SPARQL VALUES blocks for QIDs and image URLs
        value_qids = " ".join(f"wd:{qid}" for qid in instrument_qids)
        if exclude_image_urls:
            value_excludes = ", ".join(f"<{url}>" for url in exclude_image_urls)
            filter_block = f"FILTER ( ?ps_ NOT IN ( {value_excludes} ) )"
        else:
            filter_block = ""

        filter_block = ""
        query = (
            "SELECT ?instrument ?ps_Label WHERE {\n"
            f"    VALUES ?instrument {{ {value_qids} }}\n"
            "    ?instrument p:P18 ?statement .\n"
            "    ?statement ?ps ?ps_ .\n"
            "    ?wd wikibase:claim ?p;\n"
            "        wikibase:statementProperty ?ps.\n"
            '    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }\n'
            f"    {filter_block}\n"
            "}\n"
        )

        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": query, "format": "json"},
            headers=HEADERS,
            timeout=20,
        )

        if not response.ok:
            return {}

        data = response.json()

        result: dict[str, list[str]] = {qid: [] for qid in instrument_qids}
        for item in data.get("results", {}).get("bindings", []):
            qid = item.get("instrument", {}).get("value")
            img = item.get("ps_Label", {}).get("value")
            result[qid.split("/")[-1]].append(img)

        return result

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
        response = requests.get(url, timeout=10, headers=HEADERS)
        response_entities = response.json()["entities"]
        instrument_data = [
            self.parse_instrument_data(key, value)
            for key, value in response_entities.items()
        ]
        return instrument_data

    def create_database_objects(
        self, instrument_attrs: dict, original_img_paths: list, thumbnail_img_path: str
    ) -> None:
        """
        Given a dictionary of instrument attributes and a url to an instrument image,
        create the corresponding database objects.

        instrument_attrs [dict]: Dictionary of instrument attributes. See
            parse_instrument_data for details.
        original_img_paths [list]: List of paths to the original instrument images
        thumbnail_img_path [str]: Path to the thumbnail of the instrument image
        """
        ins_names = instrument_attrs.pop("ins_names")
        ins_aliases = instrument_attrs.pop("ins_aliases")

        # Create instrument using only the remaining valid fields
        instrument, _ = Instrument.objects.update_or_create(
            wikidata_id=instrument_attrs["wikidata_id"],
            defaults={
                "hornbostel_sachs_class": instrument_attrs["hornbostel_sachs_class"],
                "mimo_class": instrument_attrs["mimo_class"],
            },
        )

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

        img_obj = None
        for img_path in reversed(original_img_paths):
            img_obj, _ = AVResource.objects.get_or_create(
                instrument=instrument,
                type="image",
                format=img_path[0].split(".")[-1],
                url=img_path,
            )
        instrument.default_image = img_obj  # Default image is the Wikidata primarily image (first statement of p:P18)

        thumbnail_obj, _ = AVResource.objects.get_or_create(
            instrument=instrument,
            type="image",
            format=thumbnail_img_path.split(".")[-1],
            url=thumbnail_img_path,
        )
        instrument.thumbnail = thumbnail_obj
        instrument.save()

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

        # Fetch extera images from wikidata
        all_qids = [ins["instrument"].split("/")[-1] for ins in instrument_list]
        fetched_images = {}
        for i in range(0, len(all_qids), 100):
            batch_qids = all_qids[i : i + 100]
            batch_images = self.get_all_wikidata_images(
                batch_qids, exclude_image_urls=[]
            )
            fetched_images.update(batch_images)

        with open(
            "startup_data/wikidata_images.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["instrument", "image"])
            for qid, imgs in fetched_images.items():
                full_qid = "http://www.wikidata.org/entity/" + qid
                for img in imgs:
                    writer.writerow([full_qid, img])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Total images fetched from Wikidata: {sum(len(qid) for qid in fetched_images.values())}"
                )
            )

        img_dir = "instruments/images/instrument_imgs"
        with transaction.atomic():
            for ins_i in range(0, len(instrument_list), 50):
                ins_ids_subset: list[str] = [
                    ins["instrument"].split("/")[-1]
                    for ins in instrument_list[ins_i : ins_i + 50]
                ]
                ins_data: list[dict] = self.get_instrument_data(ins_ids_subset)
                for instrument_attrs, ins_id in zip(ins_data, ins_ids_subset):
                    original_img_paths = [
                        os.path.join(img_dir, "original", f"{ins_id}.png")
                    ] + [
                        os.path.join(img_dir, "original", f"{ins_id}_{i}.png")
                        for i in range(1, len(fetched_images.get(ins_id, [])))
                    ]
                    thumbnail_img_path = os.path.join(
                        img_dir, "thumbnail", f"{ins_id}.png"
                    )
                    self.create_database_objects(
                        instrument_attrs, original_img_paths, thumbnail_img_path
                    )
