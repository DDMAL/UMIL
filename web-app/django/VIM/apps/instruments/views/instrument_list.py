from typing import Union
import logging

import pysolr
import requests
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.views.generic import TemplateView

from VIM.apps.instruments.models import Language

logger = logging.getLogger(__name__)


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
        umil_label_name_field = f"instrument_umil_label_{lang_code}_s"
        self.instrumentname_set = InstrumentNameSet(
            data.get(name_field, []), data.get(umil_label_name_field, None)
        )


class ThumbnailStub:
    def __init__(self, url: Union[str, None]):
        self.url = url  # e.g., "instruments/images/instrument_imgs/thumbnail/Q6607.png"


class InstrumentNameStub:
    def __init__(self, name: str, umil_label_name: str = None):
        self.name = name
        self.umil_label = (self.name == umil_label_name) if umil_label_name else False


class InstrumentNameSet:
    def __init__(self, names: Union[list[str], str], umil_label_name: str = None):
        self._names = names if isinstance(names, list) else [names]
        self._umil_label_name = umil_label_name

    def all(self) -> list[InstrumentNameStub]:
        return [InstrumentNameStub(name, self._umil_label_name) for name in self._names]

    def get_display_names_str(self) -> str:
        sorted_names = sorted(self.all(), key=lambda x: not x.umil_label)
        name_list = [n.name for n in sorted_names]
        return " | ".join(name_list)


class InstrumentList(TemplateView):
    """
    Provides a paginated list of all instruments using Solr for unified pagination.

    Supports:
    - Text search queries via 'query' parameter
    - HBS classification filtering via 'hbs_facet' parameter
    - Combined search + HBS filtering (e.g., ?query=violin&hbs_facet=3)
    - Language filtering (automatically applied based on active language)
    - Pagination via 'page' and 'paginate_by' parameters (defaults to 20 per page)
    - Context-aware HBS facets (show counts for current search results)

    All queries are handled through Solr for consistent performance and functionality.
    Uses Solr filter queries (fq) to enable combining text search with classification filters.
    """

    template_name = "instruments/index.html"
    context_object_name = "instruments"

    def get_paginate_by(self) -> int:
        """Get the number of items to show per page."""
        pag_by_param: str = self.request.GET.get(
            "paginate_by", str(settings.DEFAULT_PAGE_SIZE)
        )
        try:
            paginate_by = int(pag_by_param)
        except ValueError:
            paginate_by = settings.DEFAULT_PAGE_SIZE
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
        return self.request.session.get("active_language_en", settings.DEFAULT_LANGUAGE)

    def get_active_language(self) -> Language:
        """
        Returns the active Language object.

        Returns:
            Language: The active Language object
        """
        language_en = self.get_active_language_en_label()
        try:
            return Language.objects.get(en_label=language_en)
        except Language.DoesNotExist:
            logger.error(f"Language not found: {language_en}")
            raise

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get pagination data
        page_size = self.get_paginate_by()
        (
            paginator,
            page,
            instruments,
            has_other_pages,
            facet_data,
        ) = self._paginate_solr_results(page_size)

        # Add pagination data to context
        context["paginator"] = paginator
        context["page_obj"] = page
        context["instruments"] = instruments
        context["is_paginated"] = has_other_pages

        # Add basic context data
        context["active_tab"] = "instruments"
        context["instrument_num"] = paginator.count
        context["languages"] = Language.objects.all().order_by("en_label")
        context["active_language"] = self.get_active_language()

        # Get current filter parameters
        hbs_facet = self.request.GET.get("hbs_facet", None)
        search_query = self.request.GET.get("query", "").strip()

        # Set filter state in context
        context["hbs_facet"] = hbs_facet
        context["search_query"] = search_query if search_query else None

        # Get contextual HBS facets (respects current search)
        hbs_facet_list = self._get_contextual_hbs_facets(facet_data)
        context["hbs_facets"] = hbs_facet_list

        # Get HBS facet name for display
        if hbs_facet:
            context["hbs_facet_name"] = next(
                (x["name"] for x in hbs_facet_list if x["value"] == hbs_facet), ""
            )

        # Add sort data to context
        sort_order = self.request.GET.get("sort", "").lower()
        if sort_order not in ("asc", "desc"):
            sort_order = None

        context["sort"] = sort_order

        # Add combined filter state for UI
        context["has_filters"] = bool(search_query or hbs_facet or sort_order)
        context["active_filters"] = {
            "search": search_query if search_query else None,
            "hbs_classification": (
                {"value": hbs_facet, "name": context.get("hbs_facet_name", "")}
                if hbs_facet
                else None
            ),
            "sort": (
                "Ascending"
                if sort_order == "asc"
                else "Descending"
                if sort_order == "desc"
                else None
            ),
        }

        # Add URL building helpers for preserving search query in HBS facet links
        context["current_search_query"] = search_query

        # Enhanced HBS facets with proper URLs that preserve search query
        enhanced_hbs_facets = []
        for facet in hbs_facet_list:
            facet_copy = facet.copy()

            # Build base params list
            params = []
            clear_params = []

            if search_query:
                params.append(f"query={requests.utils.quote(search_query)}")
                clear_params.append(f"query={requests.utils.quote(search_query)}")

            if sort_order:
                params.append(f"sort={sort_order}")

            # Current facet is added to main URL
            params.append(f"hbs_facet={facet['value']}")

            facet_copy["url"] = "?" + "&".join(params)
            facet_copy["clear_url"] = (
                "?" + "&".join(clear_params) if clear_params else "?"
            )

            # Add active state for current HBS filter
            facet_copy["is_active"] = facet["value"] == hbs_facet
            enhanced_hbs_facets.append(facet_copy)
        context["hbs_facets"] = enhanced_hbs_facets

        # Add clear filter URLs for UI
        params = {}
        if search_query:
            params["query"] = search_query
        if hbs_facet:
            params["hbs_facet"] = hbs_facet
        if sort_order:
            params["sort"] = sort_order

        # clear_search_url: remove 'query'
        clear_search_params = {k: v for k, v in params.items() if k != "query"}
        context["clear_search_url"] = (
            "?"
            + "&".join(
                [
                    f"{k}={requests.utils.quote(str(v))}"
                    for k, v in clear_search_params.items()
                ]
            )
            if clear_search_params
            else "?"
        )
        # clear_hbs_url: remove 'hbs_facet'
        clear_hbs_params = {k: v for k, v in params.items() if k != "hbs_facet"}
        context["clear_hbs_url"] = (
            "?"
            + "&".join(
                [
                    f"{k}={requests.utils.quote(str(v))}"
                    for k, v in clear_hbs_params.items()
                ]
            )
            if clear_hbs_params
            else "?"
        )
        # clear_sort_url: remove 'sort'
        clear_sort_params = {k: v for k, v in params.items() if k != "sort"}
        context["clear_sort_url"] = (
            "?"
            + "&".join(
                [
                    f"{k}={requests.utils.quote(str(v))}"
                    for k, v in clear_sort_params.items()
                ]
            )
            if clear_sort_params
            else "?"
        )
        # clear_all_filters_url: remove everything
        context["clear_all_filters_url"] = "?"

        return context

    def _get_solr_connection(self):
        """Get a Solr connection."""
        return pysolr.Solr(settings.SOLR_URL, timeout=settings.SOLR_TIMEOUT)

    def _build_sort_param(self, lang_code: str) -> str | None:
        """
        Builds a Solr sort expression that:
        - puts missing labels FIRST
        - sorts alphabetically by language-specific UMIL label
        """
        sort_order = self.request.GET.get("sort", "").lower()
        if sort_order not in ("asc", "desc"):
            return None

        umil_label_field = f"instrument_umil_label_{lang_code}_s"

        if sort_order == "desc":
            return (
                f"if(exists({umil_label_field}),1,0) asc, "
                f"{umil_label_field} {sort_order}"
            )
        elif sort_order == "asc":
            return f"{umil_label_field} {sort_order}"
        else:
            pass

    def _build_solr_query(self, language: Language, include_facets: bool = False):
        """Build Solr query parameters supporting combined search + HBS filtering."""
        lang_code = language.wikidata_code
        name_field = f"instrument_name_{lang_code}_ss"

        # Get request parameters
        search_query = self.request.GET.get("query", "").strip()
        hbs_facet = self.request.GET.get("hbs_facet", None)

        # Build main query (q parameter)
        if search_query:
            # Text search query
            main_query = search_query
        else:
            # Show all instruments when no text search
            main_query = "*:*"

        # Build filter queries (fq parameter) for HBS classification
        filter_queries = []
        if hbs_facet:
            filter_queries.append(f"hbs_prim_cat_s:{hbs_facet}")

        # Build sorting filter
        sort_param = self._build_sort_param(lang_code)

        umil_label_field = f"instrument_umil_label_{lang_code}_s"

        params = {
            "q": main_query,
            "wt": "json",
            "facet": "true" if include_facets else "false",
            "fl": f"sid, {name_field}, {umil_label_field}, hornbostel_sachs_class_s, mimo_class_s, thumbnail_url",
            "lang_code": lang_code,
        }

        # Add facet parameters if requested
        if include_facets:
            params["facet.pivot"] = "hbs_prim_cat_s,hbs_prim_cat_label_s"

        # Add filter queries if any
        if filter_queries:
            params["fq"] = filter_queries

        # Add sort if any
        if sort_param:
            params["sort"] = sort_param

        return params

    def _get_solr_page_results(
        self, solr, query_params: dict, page_size: int, start: int
    ):
        """Get a specific page of Solr search results with filter queries and total count."""
        solr_params = {
            **query_params,
            "rows": page_size,
            "start": start,
        }
        # Remove our custom params
        lang_code = solr_params.pop("lang_code")

        solr_response = solr.search(**solr_params)
        instruments = [
            SolrInstrument(doc, lang_code=lang_code) for doc in solr_response.docs
        ]
        total_count = solr_response.hits  # pysolr's hits corresponds to Solr's numFound

        # Return facet data if available
        facet_data = None
        if hasattr(solr_response, "facets") and solr_response.facets:
            facet_data = solr_response.facets.get("facet_pivot", {}).get(
                "hbs_prim_cat_s,hbs_prim_cat_label_s", []
            )

        return instruments, total_count, facet_data

    def _get_contextual_hbs_facets(self, contextual_facet_data):
        """Get HBS facets showing all categories with contextual counts (including zero)."""
        # Get Solr connection
        solr = self._get_solr_connection()

        # Step 1: Get ALL possible HBS categories (complete taxonomy)
        all_categories_response = solr.search(
            q="*:*",
            rows=0,
            facet="true",
            **{"facet.pivot": "hbs_prim_cat_s,hbs_prim_cat_label_s"},
        )
        all_categories_data = all_categories_response.facets["facet_pivot"][
            "hbs_prim_cat_s,hbs_prim_cat_label_s"
        ]

        # Create base list with all categories
        all_facets = {}
        for hbs_cat in all_categories_data:
            value = (
                settings.EMPTY_HBS_CATEGORY
                if hbs_cat["value"] == ""
                else hbs_cat["value"]
            )
            name = hbs_cat["pivot"][0]["value"]
            all_facets[value] = {
                "value": value,
                "name": name,
                "count": 0,  # Default to 0, will update with contextual counts
            }

        # Step 2: Use contextual facet data from main query (if available)
        if contextual_facet_data:
            # Update counts with contextual data from main search query
            for hbs_cat in contextual_facet_data:
                value = (
                    settings.EMPTY_HBS_CATEGORY
                    if hbs_cat["value"] == ""
                    else hbs_cat["value"]
                )
                if value in all_facets:
                    all_facets[value]["count"] = hbs_cat["count"]
        else:
            # No contextual facet data, use the all categories counts directly
            for hbs_cat in all_categories_data:
                value = (
                    settings.EMPTY_HBS_CATEGORY
                    if hbs_cat["value"] == ""
                    else hbs_cat["value"]
                )
                if value in all_facets:
                    all_facets[value]["count"] = hbs_cat["count"]

        # Convert to list and sort
        hbs_facet_list = sorted(
            all_facets.values(), key=lambda x: (x["name"] == "Unclassified", x["value"])
        )

        return hbs_facet_list

    def _paginate_solr_results(self, page_size):
        """Handle Solr pagination for all query types (search, HBS filter, show all)."""
        language = self.get_active_language()
        page_number = int(self.request.GET.get("page", 1))
        start = (page_number - 1) * page_size

        # Get Solr connection and query parameters with facets enabled
        solr = self._get_solr_connection()
        query_params = self._build_solr_query(language, include_facets=True)

        # Get page results, total count, and facet data in one query
        page_results, total_count, facet_data = self._get_solr_page_results(
            solr, query_params, page_size, start
        )

        # Create paginator and page objects
        paginator = SolrPaginator(page_results, page_size, total_count)
        page = Page(page_results, page_number, paginator)

        return (paginator, page, page_results, page.has_other_pages(), facet_data)

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)
