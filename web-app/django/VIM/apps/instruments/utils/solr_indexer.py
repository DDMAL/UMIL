"""Utility functions for Solr search index management."""

import logging
import pysolr
from django.conf import settings
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import Case, CharField, F, When
from django.db.models import Value as V
from django.db.models.functions import Concat, Left, JSONObject

logger = logging.getLogger(__name__)

HBS_LABEL_MAP = {
    "1": "Idiophones",
    "2": "Membranophones",
    "3": "Chordophones",
    "4": "Aerophones",
    "5": "Electrophones",
    settings.EMPTY_HBS_CATEGORY: "Unclassified",
}


def get_solr_connection():
    """Get a Solr connection instance."""
    return pysolr.Solr(settings.SOLR_URL, timeout=10, always_commit=True)


def index_single_instrument(instrument_id: int) -> bool:
    """
    Index a single instrument in Solr.

    Args:
        instrument_id: Primary key of the instrument to index

    Returns:
        bool: True if successful, False otherwise
    """
    from VIM.apps.instruments.models import Instrument

    try:
        # Query with all necessary annotations (same as index_data.py)
        instrument_qs = (
            Instrument.objects.filter(pk=instrument_id)
            .annotate(
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
            )
            .values(
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

        if not instrument_qs.exists():
            logger.error(f"Instrument {instrument_id} not found for indexing")
            return False

        instrument_data = list(instrument_qs)[0]

        # Process HBS label (same logic as index_data.py)
        hbs_code = instrument_data.get("hbs_prim_cat_s")
        instrument_data["hbs_prim_cat_label_s"] = HBS_LABEL_MAP.get(hbs_code, "")

        # Process instrument names by language
        for name_entry in instrument_data.pop("instrument_names_by_language", []):
            instrument_name_field = f"instrument_name_{name_entry['lang']}_ss"
            instrument_umil_label_field = (
                f"instrument_umil_label_{name_entry['lang']}_s"
            )

            if instrument_name_field not in instrument_data:
                instrument_data[instrument_name_field] = [name_entry["name"]]
            else:
                instrument_data[instrument_name_field].append(name_entry["name"])

            if name_entry.get("umil_label"):
                instrument_data[instrument_umil_label_field] = name_entry["name"]

        # Add to Solr
        solr = get_solr_connection()
        solr.add([instrument_data])

        logger.info(f"Successfully indexed instrument {instrument_id} in Solr")
        return True

    except Exception as e:
        logger.error(
            f"Failed to index instrument {instrument_id} in Solr: {e}", exc_info=True
        )
        return False


def delete_instrument_from_solr(instrument_id: int) -> bool:
    """
    Delete a single instrument from Solr index.

    Args:
        instrument_id: Primary key of the instrument to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        solr = get_solr_connection()
        doc_id = f"instrument-{instrument_id}"
        solr.delete(id=doc_id)
        logger.info(f"Successfully deleted instrument {instrument_id} from Solr")
        return True
    except Exception as e:
        logger.error(
            f"Failed to delete instrument {instrument_id} from Solr: {e}", exc_info=True
        )
        return False
