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

        # Query the instrument names in all languages
        context["instrument_names"] = (
            context["instrument"].instrumentname_set.all().select_related("language")
        )

        # Get the active language
        active_language_en = self.request.session.get("active_language_en", None)
        context["active_language"] = (
            Language.objects.get(en_label=active_language_en)
            if active_language_en
            else Language.objects.get(en_label="english")  # default in English
        )
        return context
