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
        hbs_facets = requests.get(
            "http://solr:8983/solr/virtual-instrument-museum/select?facet.pivot=hbs_prim_cat_label_s,hbs_sec_cat_label_s&facet=true&indent=true&q=*:*&rows=0"
        ).json()["facet_counts"]["facet_pivot"][
            "hbs_prim_cat_label_s,hbs_sec_cat_label_s"
        ]
        hbs_facet_list = []
        for hbs_prim_cat in hbs_facets:
            hbs_facet_list.append(
                {
                    hbs_prim_cat["value"]: hbs_prim_cat["count"],
                    "children": {
                        hbs_sec_cat["value"]: hbs_sec_cat["count"]
                        for hbs_sec_cat in hbs_prim_cat["pivot"]
                    },
                }
            )
        context["hbs_facets"] = hbs_facet_list
        return context

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)
