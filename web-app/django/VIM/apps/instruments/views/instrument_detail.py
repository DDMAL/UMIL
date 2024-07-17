from django.views.generic import DetailView
from VIM.apps.instruments.models import Instrument


class InstrumentDetail(DetailView):
    """
    Displays details of a specific instrument.
    """

    model = Instrument
    template_name = "instruments/detail.html"
    context_object_name = "instrument"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = self.get_object()

        context["wikidata_id"] = instrument.wikidata_id
        context["default_image_url"] = (
            instrument.default_image.url if instrument.default_image else None
        )
        context["hornbostel_sachs_class"] = instrument.hornbostel_sachs_class
        context["mimo_class"] = instrument.mimo_class

        # Get english name
        context["instrument_name_en"] = instrument.instrumentname_set.get(
            language__en_label="english"
        ).name

        # Get all instrument names in all languages
        instrument_names = []
        for instrument_name in instrument.instrumentname_set.all():
            instrument_names.append(
                {
                    "name": instrument_name.name,
                    "source_name": instrument_name.source_name,
                    "language_code": instrument_name.language.wikidata_code,
                    "language_id": instrument_name.language.wikidata_id,
                    "language_en_label": instrument_name.language.en_label,
                    "language_autonym": instrument_name.language.autonym,
                }
            )
        context["instrument_names"] = instrument_names

        return context
