from django.views.generic import ListView
from VIM.apps.instruments.models import Instrument


class InstrumentList(ListView):
    template_name = "instrument_list.html"
    context_object_name = "instruments"
    model = Instrument
