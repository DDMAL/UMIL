from typing import Union
import logging

import pysolr
import requests
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db.models import Prefetch, QuerySet
from django.views.generic import ListView

from VIM.apps.instruments.models import Instrument, InstrumentName, Language

logger = logging.getLogger(__name__)

# Constants
SOLR_SEARCH_MARKER = "SOLR_SEARCH"


# Custom paginator for Solr search results
class SolrPaginator(Paginator):
    """Custom paginator that knows the total count of Solr results."""

    def __init__(self, object_list, per_page, total_count):
        super().__init__(object_list, per_page)
        self._count = total_count

    @property
    def count(self):
        return self._count


# Helper classes to normalize Solr results
class SolrInstrument:
    def __init__(self, data: dict, lang_code: str = "en"):
        sid = data.get("sid")
        self.pk = sid.replace("instrument-", "") if sid else ""
        self.thumbnail = ThumbnailStub(data.get("thumbnail_url"))
        name_field = f"instrument_name_{lang_code}_ss"
        self.instrumentname_set = InstrumentNameSet(data.get(name_field, []))


class ThumbnailStub:
    def __init__(self, url: Union[str, None]):
        self.url = url  # e.g., "instruments/images/instrument_imgs/thumbnail/Q6607.png"


class InstrumentNameStub:
    def __init__(self, name: str):
        self.name = name


class InstrumentNameSet:
    def __init__(self, names: Union[list[str], str]):
        self._names = names if isinstance(names, list) else [names]

    def all(self) -> list[InstrumentNameStub]:
        return [InstrumentNameStub(name) for name in self._names]


class InstrumentList(ListView):
    """
    Provides a paginated list of all instruments in the database.

    Pass `page` and `paginate_by` as query parameters to control pagination.
    Defaults to 20 instruments per page.
    """

    template_name = "instruments/index.html"
    context_object_name = "instruments"

    def get_paginate_by(self, queryset) -> int:
        pag_by_param: str = self.request.GET.get("paginate_by", "20")
        try:
            paginate_by = int(pag_by_param)
        except ValueError:
            paginate_by = 20
        return paginate_by

    def get_active_language_en_label(self) -> str:
        """
        Returns the English label of the active language.

        The active language is determined by the following order of precedence:
            - by the `language` query parameter if present
            - by the `active_language_en` session variable if present
            - by the default language 'english'

        Returns:
            str: The English label of the active language
        """
        language_en = self.request.GET.get("language")
        if language_en:
            return language_en
        return self.request.session.get("active_language_en", "English")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "instruments"
        context["instrument_num"] = context["paginator"].count
        context["languages"] = Language.objects.all().order_by("en_label")
        active_language_en = self.get_active_language_en_label()
        context["active_language"] = Language.objects.get(en_label=active_language_en)

        hbs_facet = self.request.GET.get("hbs_facet", None)
        context["hbs_facet"] = hbs_facet

        hbs_facets = requests.get(
            (
                "http://solr:8983/solr/virtual-instrument-museum/select?"
                "facet.pivot=hbs_prim_cat_s,hbs_prim_cat_label_s"
                "&facet=true&indent=true&q=*:*&rows=0"
            ),
            timeout=10,
        ).json()["facet_counts"]["facet_pivot"]["hbs_prim_cat_s,hbs_prim_cat_label_s"]
        hbs_facet_list = []
        for hbs_cat in hbs_facets:
            hbs_facet_list.append(
                {
                    "value": "999" if hbs_cat["value"] == "" else hbs_cat["value"],
                    "name": hbs_cat["pivot"][0]["value"],
                    "count": hbs_cat["count"],
                }
            )
        hbs_facet_list.sort(key=lambda x: x["value"])
        context["hbs_facets"] = hbs_facet_list
        if hbs_facet:
            context["hbs_facet_name"] = next(
                (x["name"] for x in hbs_facet_list if x["value"] == hbs_facet), ""
            )
        search_query = self.request.GET.get("query", "").strip()
        if search_query:
            context["search_query"] = search_query
        return context

    def _get_solr_connection(self):
        """Get a Solr connection with error handling."""
        try:
            return pysolr.Solr(settings.SOLR_URL, timeout=10)
        except Exception as e:
            logger.error(f"Failed to connect to Solr: {e}")
            raise

    def _get_solr_search_params(self, search_query: str, language_en: str):
        """Get common Solr search parameters."""
        try:
            lang_code = Language.objects.get(en_label=language_en).wikidata_code
            name_field = f"instrument_name_{lang_code}_ss"
            return {
                "q": search_query,
                "wt": "json",
                "facet": "false",
                "fl": f"sid, {name_field}, hornbostel_sachs_class_s, mimo_class_s, thumbnail_url",
                "lang_code": lang_code,
            }
        except Language.DoesNotExist:
            logger.error(f"Language not found: {language_en}")
            raise

    def _get_solr_total_count(self, solr, search_query: str):
        """Get total count of Solr search results."""
        try:
            count_params = {
                "q": search_query,
                "wt": "json",
                "rows": 0,  # We only want the count
                "facet": "false",
            }
            count_response = solr.search(**count_params)
            return count_response.hits
        except Exception as e:
            logger.error(f"Failed to get Solr count for query '{search_query}': {e}")
            return 0

    def _get_solr_page_results(
        self, solr, search_params: dict, page_size: int, start: int
    ):
        """Get a specific page of Solr search results."""
        try:
            solr_params = {
                **search_params,
                "rows": page_size,
                "start": start,
            }
            # Remove our custom params
            lang_code = solr_params.pop("lang_code")

            solr_response = solr.search(**solr_params)
            return [
                SolrInstrument(doc, lang_code=lang_code) for doc in solr_response.docs
            ]
        except Exception as e:
            logger.error(f"Failed to get Solr page results: {e}")
            return []

    def paginate_queryset(self, queryset, page_size):
        """Custom pagination to handle Solr search results."""
        if queryset == SOLR_SEARCH_MARKER:
            return self._paginate_solr_search(page_size)

        # Use default pagination for regular querysets
        return super().paginate_queryset(queryset, page_size)

    def _paginate_solr_search(self, page_size):
        """Handle Solr search pagination."""
        search_query = self.request.GET.get("query", "").strip()
        language_en = self.get_active_language_en_label()
        page_number = int(self.request.GET.get("page", 1))
        start = (page_number - 1) * page_size

        # Get Solr connection and search parameters
        solr = self._get_solr_connection()
        search_params = self._get_solr_search_params(search_query, language_en)

        # Get total count and page results
        total_results = self._get_solr_total_count(solr, search_query)
        page_results = self._get_solr_page_results(
            solr, search_params, page_size, start
        )

        # Create paginator and page objects
        paginator = SolrPaginator(page_results, page_size, total_results)
        page = Page(page_results, page_number, paginator)

        return (paginator, page, page_results, page.has_other_pages())

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> Union[QuerySet[Instrument], list[SolrInstrument]]:
        language_en = self.get_active_language_en_label()
        instrumentname_prefetch_manager = Prefetch(
            "instrumentname_set",
            queryset=InstrumentName.objects.filter(language__en_label=language_en),
        )
        hbs_facet = self.request.GET.get("hbs_facet", None)
        if hbs_facet:
            return (
                Instrument.objects.filter(hornbostel_sachs_class__startswith=hbs_facet)
                .select_related("thumbnail")
                .prefetch_related(instrumentname_prefetch_manager)
            )

        search_query = self.request.GET.get("query", "").strip()

        if search_query:
            # Return a special marker for Solr search that will be handled in paginate_queryset
            return SOLR_SEARCH_MARKER

        return Instrument.objects.select_related("thumbnail").prefetch_related(
            instrumentname_prefetch_manager
        )
