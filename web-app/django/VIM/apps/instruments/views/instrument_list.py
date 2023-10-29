from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument, Language
import requests


class InstrumentList(ListView):
    """
    Provides a paginated list of all instruments in the database.

    Pass `page` and `paginate_by` as query parameters to control pagination.
    Defaults to 20 instruments per page.
    """

    template_name = "instruments/index.html"
    context_object_name = "instruments"
    model = Instrument

    def get_paginate_by(self, queryset) -> int:
        pag_by_param: str = self.request.GET.get("paginate_by", "20")
        try:
            paginate_by = int(pag_by_param)
        except ValueError:
            paginate_by = 20
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "instruments"
        context["instrument_num"] = Instrument.objects.count()
        context["languages"] = Language.objects.all()
        active_language_en = self.request.session.get("active_language_en", None)
        context["active_language"] = (
            Language.objects.get(en_label=active_language_en)
            if active_language_en
            else Language.objects.get(en_label="english")  # default in English
        )
        active_language_code = context["active_language"].wikidata_code

        hbs_facet = self.request.GET.get("hbs_facet", None)
        context["hbs_facet"] = hbs_facet

        hbs_facets = requests.get(
            f"http://solr:8983/solr/virtual-instrument-museum/select?facet.pivot=hbs_prim_cat_s,hbs_prim_cat_label_{active_language_code}_s&facet=true&indent=true&q=*:*&rows=0"
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
        context["hbs_facet_name"] = hbs_facet_list[int(hbs_facet) - 1]["name"]
        return context

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        hbs_facet = self.request.GET.get("hbs_facet", None)
        if hbs_facet:
            return Instrument.objects.filter(
                hornbostel_sachs_class__startswith=hbs_facet
            )
        return super().get_queryset()
