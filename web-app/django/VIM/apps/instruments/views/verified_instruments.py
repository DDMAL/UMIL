from django.utils import timezone
from django.views.generic.list import ListView

from VIM.apps.instruments.models import InstrumentName

class InstrumentNameListView(ListView):
    model = InstrumentName
    template_name = "instruments/name_list.html"
    paginate_by = 100  # if pagination is desired
    context_object_name = "instrument_names"

    def get_queryset(self):
        return InstrumentName.objects.filter(status="verified")