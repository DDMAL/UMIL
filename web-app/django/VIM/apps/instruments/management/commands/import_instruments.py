import csv
import requests
from django.core.management.base import BaseCommand
from django.db.utils import DataError
from django.db import transaction
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource
from typing import Union

# For now, we only import instrument language names in these
# two languages.
LANGUAGES = "en|fr"


class Command(BaseCommand):
    help = "Imports instrument objects"

    def parse_instrument_data(self, instrument_id: str, instrument_data: dict) -> dict:
        # Get available instrument names
        ins_labels: dict = instrument_data["labels"]
        ins_names = dict(
            [(value["language"], value["value"]) for key, value in ins_labels.items()]
        )
        # Get Hornbostel-Sachs and MIMO classifications, if available
        ins_hbs: Union[dict, None] = instrument_data["claims"].get("P1762", "")
        ins_mimo: Union[dict, None] = instrument_data["claims"].get("P3763", "")
        if ins_hbs:
            if ins_hbs[0]["mainsnak"]["snaktype"] == "value":
                ins_hbs = ins_hbs[0]["mainsnak"]["datavalue"]["value"]
            else:
                ins_hbs = ""
        if ins_mimo:
            if ins_mimo[0]["mainsnak"]["snaktype"] == "value":
                ins_mimo = ins_mimo[0]["mainsnak"]["datavalue"]["value"]
            else:
                ins_mimo = ""
        parsed_data = {
            "wikidata_id": instrument_id,
            "ins_names": ins_names,
            "hornbostel_sachs_class": ins_hbs,
            "mimo_class": ins_mimo,
        }
        return parsed_data

    def get_instrument_data(self, instrument_ids: list[str]) -> list[dict]:
        ins_ids_str: str = "|".join(instrument_ids)
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ins_ids_str}&format=json&props=labels|descriptions|claims&languages={LANGUAGES}"
        response = requests.get(url)
        response_entities = response.json()["entities"]
        instrument_data = [
            self.parse_instrument_data(key, value)
            for key, value in response_entities.items()
        ]
        return instrument_data

    def handle(self, *args, **options):
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
                            source_type="Wikidata",
                            source_date="2023-09-21",
                            source_description="",
                        )
                    ins_img = ins_imgs_subset[idx]
                    AVResource.objects.create(
                        instrument=instrument,
                        type="image",
                        format=ins_img.split(".")[-1],
                        uri=ins_img,
                    )
