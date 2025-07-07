from django.utils import timezone
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin

from VIM.apps.instruments.models import InstrumentName

class InstrumentNameListView(UserPassesTestMixin, ListView):
    model = InstrumentName
    template_name = "instruments/upload.html"
    paginate_by = 100  # if pagination is desired
    context_object_name = "instrument_names"

    def get_queryset(self):
        return InstrumentName.objects.filter(is_approved=True, on_wikidata=False)
    
    def test_func(self):
        return self.request.user.is_superuser