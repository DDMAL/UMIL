from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
import requests


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
        context["languages"] = Language.objects.all()
        active_language_en = self.get_active_language_en_label()
        context["active_language"] = Language.objects.get(en_label=active_language_en)
        active_language_code = context["active_language"].wikidata_code

        hbs_facet = self.request.GET.get("hbs_facet", None)
        context["hbs_facet"] = hbs_facet

        hbs_facets = requests.get(
            (
                "http://solr:8983/solr/virtual-instrument-museum/select?"
                f"facet.pivot=hbs_prim_cat_s,hbs_prim_cat_label_{active_language_code}_s"
                "&facet=true&indent=true&q=*:*&rows=0"
            ),
            timeout=10,
        ).json()["facet_counts"]["facet_pivot"][
            f"hbs_prim_cat_s,hbs_prim_cat_label_{active_language_code}_s"
        ]
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
        return context

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Instrument]:
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
        return Instrument.objects.select_related("thumbnail").prefetch_related(
            instrumentname_prefetch_manager
        )
