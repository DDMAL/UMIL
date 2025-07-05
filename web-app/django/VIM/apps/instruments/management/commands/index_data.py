"""This module indexes instrument data in the database in Solr."""

from django.core.management.base import BaseCommand
from django.db.models import F, CharField, Value as V
from django.db.models.functions import Concat, Left
import requests
from VIM.apps.instruments.models import Instrument, Language


class Command(BaseCommand):
    """
    The index_data command indexes instrument data in the database in Solr.
    """

    help = "Indexes instrument data in the database in Solr."

    def handle(self, *args, **options):
        instruments = list(
            Instrument.objects.all().values(
                sid=Concat(V("instrument-"), "id", output_field=CharField()),
                wikidata_id_s=F("wikidata_id"),
                hornbostel_sachs_class_s=F("hornbostel_sachs_class"),
                hbs_prim_cat_s=Left(F("hornbostel_sachs_class"), 1),
                mimo_class_s=F("mimo_class"),
                type=V("instrument"),
            )
        )
        languages = Language.objects.all().values_list("wikidata_code", flat=True)
        hbs_label_map = self.build_hbs_label_map()
        for instrument in instruments:
            hbs_code = instrument["hbs_prim_cat_s"]
            for lang_code in languages:
                label = hbs_label_map.get(lang_code, {}).get(hbs_code, "")
                instrument[f"hbs_prim_cat_label_{lang_code}_s"] = label
        requests.post(
            "http://solr:8983/solr/virtual-instrument-museum/update?commit=true",
            json=instruments,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

    def build_hbs_label_map(self):
        """Build a mapping of Hornbostel-Sachs classification codes to labels."""
        # For now, we just want the names in English and French of the first category of
        # the Hornbostel-Sachs classification.
        eng_name_mapping = {
            "1": "Idiophones",
            "2": "Membranophones",
            "3": "Chordophones",
            "4": "Aerophones",
            "5": "Electrophones",
        }
        fr_name_mapping = {
            "1": "Idiophones",
            "2": "Membranophones",
            "3": "Cordophones",
            "4": "Aérophones",
            "5": "Électrophones",
        }
        hbs_label_map = {"en": eng_name_mapping, "fr": fr_name_mapping}
        # for all other languages, we will use the English names (temporarily)
        for lang_code in Language.objects.exclude(
            wikidata_code__in=["en", "fr"]
        ).values_list("wikidata_code", flat=True):
            hbs_label_map[lang_code] = eng_name_mapping.copy()
        return hbs_label_map
        # top_concepts = requests.get(
        #     "https://vocabulary.mimo-international.com/rest/v1/HornbostelAndSachs/topConcepts"
        # ).json()["topconcepts"]
        # hbs_label_map = {}
        # for t_c in top_concepts:
        #     hbs_label_map[t_c["notation"]] = t_c["label"]
        #     child_concepts = requests.get(
        #         "https://vocabulary.mimo-international.com/rest/v1/HornbostelAndSachs/children?uri="
        #         + t_c["uri"]
        #     ).json()["narrower"]
        #     for c_c in child_concepts:
        #         hbs_label_map[c_c["notation"]] = c_c["prefLabel"]
        # return hbs_label_map
