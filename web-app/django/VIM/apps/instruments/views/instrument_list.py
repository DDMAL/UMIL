from typing import Any
from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument


class InstrumentList(ListView):
    template_name = "instruments/index.html"
    context_object_name = "instruments"
    model = Instrument

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get("paginate_by", None)
        if paginate_by is not None:
            return paginate_by
        return 20