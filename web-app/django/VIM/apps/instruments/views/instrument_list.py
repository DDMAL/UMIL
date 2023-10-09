from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument


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
        context['instrument_num'] = Instrument.objects.count()
        return context
