from django.views.generic import DetailView
from VIM.apps.instruments.models import Instrument, Language

class InstrumentDetail(DetailView):
    """
    Displays details of a specific instrument.
    """

    model = Instrument
    template_name = "instruments/detail.html"
    context_object_name = "instrument"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'language__en_label')

        instrument_names = context["instrument"].instrumentname_set.all().select_related("language")

        if search_query:
            instrument_names = instrument_names.filter(language__en_label__icontains=search_query)

        instrument_names = instrument_names.order_by(sort_by)
        context["instrument_names"] = instrument_names

        # Get the active language
        active_language_en = self.request.session.get("active_language_en", None)
        context["active_language"] = (
            Language.objects.get(en_label=active_language_en)
            if active_language_en
            else Language.objects.get(en_label="english")  # default in English
        )
        return context
