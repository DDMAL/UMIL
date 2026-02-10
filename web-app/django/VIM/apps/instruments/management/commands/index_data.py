"""This module indexes instrument data in the database in Solr."""

import pysolr
from django.conf import settings
from django.contrib.postgres.aggregates import JSONBAgg
from django.core.management.base import BaseCommand
from django.db.models import Case, CharField, F, When
from django.db.models import Value as V
from django.db.models.functions import Concat, Left, JSONObject

from VIM.apps.instruments.models import Instrument


class Command(BaseCommand):
    """
    The index_data command indexes instrument data in the database in Solr.
    """

    help = "Indexes instrument data in the database in Solr."

    HBS_LABEL_MAP = {
        "1": "Idiophones",
        "2": "Membranophones",
        "3": "Chordophones",
        "4": "Aerophones",
        "5": "Electrophones",
        settings.EMPTY_HBS_CATEGORY: "Unclassified",
    }

    def handle(self, *args, **options):
        instruments = list(
            Instrument.objects.annotate(
                sid=Concat(V("instrument-"), "id", output_field=CharField()),
                umil_id_s=F("umil_id"),
                wikidata_id_s=F("wikidata_id"),
                hornbostel_sachs_class_s=F("hornbostel_sachs_class"),
                hbs_prim_cat_s=Left(F("hornbostel_sachs_class"), 1),
                mimo_class_s=F("mimo_class"),
                type=V("instrument"),
                thumbnail_url=Case(
                    When(thumbnail__file__gt="", then=F("thumbnail__file")),
                    default=F("thumbnail__url"),
                    output_field=CharField(),
                ),
                instrument_names_by_language=JSONBAgg(
                    JSONObject(
                        lang=F("instrumentname__language__wikidata_code"),
                        name=F("instrumentname__name"),
                        umil_label=F("instrumentname__umil_label"),
                    ),
                ),
            ).values(
                "sid",
                "umil_id_s",
                "wikidata_id_s",
                "hornbostel_sachs_class_s",
                "hbs_prim_cat_s",
                "mimo_class_s",
                "type",
                "thumbnail_url",
                "instrument_names_by_language",
            )
        )

        for instrument in instruments:
            hbs_code = instrument["hbs_prim_cat_s"]
            instrument["hbs_prim_cat_label_s"] = self.HBS_LABEL_MAP.get(hbs_code, "")

            for name_entry in instrument.pop("instrument_names_by_language", []):
                instrument_name_field = f"instrument_name_{name_entry['lang']}_ss"
                instrument_umil_label_field = (
                    f"instrument_umil_label_{name_entry['lang']}_s"
                )
                if instrument_name_field not in instrument:
                    instrument[instrument_name_field] = [name_entry["name"]]
                else:
                    instrument[instrument_name_field].append(name_entry["name"])
                if name_entry.get("umil_label"):
                    instrument[instrument_umil_label_field] = name_entry["name"]

        # Initialize Solr client
        solr = pysolr.Solr(settings.SOLR_URL, timeout=10, always_commit=True)

        # Add data to Solr using the pysolr client
        solr.add(instruments)

        # Clear needs_reindexing flag for all instruments after full reindex
        Instrument.objects.all().update(needs_reindexing=False)
        self.stdout.write(self.style.SUCCESS("Cleared reindexing flags"))

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
