import csv
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
    This list of instruments is stored in startup_data/vim_instruments_with_images-15sept.csv
    """

    help = "Imports instrument objects"

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
            f"ids={ins_ids_str}&format=json&props=labels|descriptions|"
            "claims&languages=en|fr"
        )
        response = requests.get(url, timeout=10)
        response_entities = response.json()["entities"]
        instrument_data = [
            self.parse_instrument_data(key, value)
            for key, value in response_entities.items()
        ]
        return instrument_data

    def handle(self, *args, **options) -> None:
        with open(
            "startup_data/vim_instruments_with_images-15sept.csv", encoding="utf-8-sig"
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            instrument_list: list[dict] = list(reader)
        language_map = Language.objects.in_bulk(field_name="wikidata_code")
        with transaction.atomic():
            for ins_i in range(0, len(instrument_list), 50):
                ins_ids_subset: list[str] = [
                    ins["instrument"].split("/")[-1]
                    for ins in instrument_list[ins_i : ins_i + 50]
                ]
                ins_data: list[dict] = self.get_instrument_data(ins_ids_subset)
                ins_imgs_subset: list[str] = [
                    ins["image"] for ins in instrument_list[ins_i : ins_i + 50]
                ]
                for idx, ins in enumerate(ins_data):
                    ins_names = ins.pop("ins_names")
                    instrument = Instrument.objects.create(**ins)
                    for lang, name in ins_names.items():
                        InstrumentName.objects.create(
                            instrument=instrument,
                            language=language_map[lang],
                            name=name,
                            source_name="Wikidata",
                        )
                    ins_img = ins_imgs_subset[idx]
                    img_obj = AVResource.objects.create(
                        instrument=instrument,
                        type="image",
                        format=ins_img.split(".")[-1],
                        url=ins_img,
                    )
                    instrument.default_image = img_obj
                    instrument.save()
