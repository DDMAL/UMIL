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
            else Language.objects.get(en_label="English")  # default in English
        )

        # Get the instrument label in the active language
        # Set label to the first instrument name added in the language if there is no "umil_label" set
        active_labels = context["instrument_names"].filter(
            language=context["active_language"]
        )
        umil_label = active_labels.filter(umil_label=True)
        if umil_label.exists():
            context["active_instrument_label"] = umil_label
        else:
            context["active_instrument_label"] = active_labels.first()

        # Get all languages for the dropdown
        context["languages"] = Language.objects.all()

        return context
