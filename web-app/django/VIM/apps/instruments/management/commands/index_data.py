"""This module indexes instrument data in the database in Solr."""

from django.core.management.base import BaseCommand
from django.db.models import F, CharField, Value as V
from django.db.models.functions import Concat, Left
import requests
from VIM.apps.instruments.models import Instrument


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
        hbs_label_map = self.build_hbs_label_map()
        for instrument in instruments:
            hbs_code = instrument["hbs_prim_cat_s"]
            instrument["hbs_prim_cat_label_s"] = hbs_label_map.get(hbs_code, "")
        requests.post(
            "http://solr:8983/solr/virtual-instrument-museum/update?commit=true",
            json=instruments,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

    def build_hbs_label_map(self):
        """
        Return HBS labels in English.
        Other languages will be handled by Google Translate.
        """
        return {
            "1": "Idiophones",
            "2": "Membranophones",
            "3": "Chordophones",
            "4": "Aerophones",
            "5": "Electrophones",
        }
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
