from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument, Language


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
        return context

    def get(self, request, *args, **kwargs):
        language_en = request.GET.get("language", None)
        if language_en:
            request.session["active_language_en"] = language_en
        return super().get(request, *args, **kwargs)
