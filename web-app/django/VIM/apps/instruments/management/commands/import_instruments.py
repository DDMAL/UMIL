"""This module imports instrument objects from Wikidata for the VIM project."""

import csv
import os
from typing import Optional
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource


class Command(BaseCommand):
    """
    The import_instruments command imports instrument objects from Wikidata.

    NOTE: For now, this script only imports instrument names in English and French. It
    also only imports a set of previously-curated instruments that have images available.
    This list of instruments is stored in startup_data/all_instruments_with_16aug_2024.csv
    """

    help = "Imports instrument objects"

    def __init__(self):
        super().__init__()
        self.language_map: dict[str, Language] = {}

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

        # Get available instrument descriptions
        ins_descriptions: dict = instrument_data["descriptions"]
        ins_descs: dict[str, str] = {
            value["language"]: value["value"] for key, value in ins_descriptions.items()
        }

        # Get available instrument aliases
        ins_aliases: dict = instrument_data["aliases"]
        ins_alias: dict[str, list[str]] = {
            key: [value["value"] for value in values]
            for key, values in ins_aliases.items()
        }

        # Get Hornbostel-Sachs and MIMO classifications, if available
        ins_hbs: Optional[list[dict]] = instrument_data["claims"].get("P1762")
        ins_mimo: Optional[list[dict]] = instrument_data["claims"].get("P3763")
        if ins_hbs and ins_hbs[0]["mainsnak"]["snaktype"] == "value":
            hbs_class: str = ins_hbs[0]["mainsnak"]["datavalue"]["value"]
        else:
            hbs_class = ""
        if ins_mimo and ins_mimo[0]["mainsnak"]["snaktype"] == "value":
            mimo_class: str = ins_mimo[0]["mainsnak"]["datavalue"]["value"]
        else:
            mimo_class = ""
        parsed_data: dict[str, str | dict[str, str]] = {
            "wikidata_id": instrument_id,
            "ins_names": ins_names,
            "ins_descs": ins_descs,
            "ins_alias": ins_alias,
            "hornbostel_sachs_class": hbs_class,
            "mimo_class": mimo_class,
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
            f"ids={ins_ids_str}&format=json&props=labels|descriptions|aliases|"
            "claims&languages=en|fr"
        )
        response = requests.get(url, timeout=10)
        response_entities = response.json()["entities"]
        instrument_data = [
            self.parse_instrument_data(key, value)
            for key, value in response_entities.items()
        ]
        return instrument_data

    def create_database_objects(
        self, instrument_attrs: dict, original_img_path: str, thumbnail_img_path: str
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
        ins_descs = instrument_attrs.pop("ins_descs")
        ins_alias = instrument_attrs.pop("ins_alias")
        instrument = Instrument.objects.create(**instrument_attrs)
        for lang, name in ins_names.items():
            description = ins_descs.get(lang, "")
            alias = ins_alias.get(lang, [])
            InstrumentName.objects.create(
                instrument=instrument,
                language=self.language_map[lang],
                description=description,
                alias=", ".join(alias),
                name=name,
                source_name="Wikidata",
            )
        img_obj = AVResource.objects.create(
            instrument=instrument,
            type="image",
            format=original_img_path.split(".")[-1],
            url=original_img_path,
        )
        instrument.default_image = img_obj
        thumbnail_obj = AVResource.objects.create(
            instrument=instrument,
            type="image",
            format=thumbnail_img_path.split(".")[-1],
            url=thumbnail_img_path,
        )
        instrument.thumbnail = thumbnail_obj
        instrument.save()

    def handle(self, *args, **options) -> None:
        with open(
            "startup_data/all_instruments_11oct_2024.csv",
            encoding="utf-8-sig",
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            instrument_list: list[dict] = list(reader)
        self.language_map = Language.objects.in_bulk(field_name="wikidata_code")
        img_dir = "instruments/images/instrument_imgs"
        with transaction.atomic():
            for ins_i in range(0, len(instrument_list), 50):
                ins_ids_subset: list[str] = [
                    ins["instrument"].split("/")[-1]
                    for ins in instrument_list[ins_i : ins_i + 50]
                ]
                ins_data: list[dict] = self.get_instrument_data(ins_ids_subset)
                for instrument_attrs, ins_id in zip(ins_data, ins_ids_subset):
                    original_img_path = os.path.join(
                        img_dir, "original", f"{ins_id}.png"
                    )
                    thumbnail_img_path = os.path.join(
                        img_dir, "thumbnail", f"{ins_id}.png"
                    )
                    self.create_database_objects(
                        instrument_attrs, original_img_path, thumbnail_img_path
                    )
