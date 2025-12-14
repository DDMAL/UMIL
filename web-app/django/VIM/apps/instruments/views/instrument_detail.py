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
        instrument_names = (
            context["instrument"]
            .instrumentname_set.all()
            .select_related("language")
            .prefetch_related("sources")
        )
        if self.request.user.is_authenticated:
            # Show all names for authenticated users
            context["instrument_names"] = instrument_names.all()
        else:
            # Show only verified names for unauthenticated users
            context["instrument_names"] = instrument_names.filter(
                verification_status="verified"
            )

        # Initialize a dictionary to store label and aliases by language
        label_aliases_dict = {}
        for instrumentname in instrument_names:
            language = instrumentname.language
            if language not in label_aliases_dict:
                label_aliases_dict[language] = {"label": None, "aliases": []}
            if instrumentname.umil_label:
                label_aliases_dict[language]["label"] = instrumentname
            else:
                label_aliases_dict[language]["aliases"].append(instrumentname)
        context["label_aliases_dict"] = label_aliases_dict

        # Get the active language
        active_language_en = self.request.session.get("active_language_en", None)
        context["active_language"] = (
            Language.objects.get(en_label=active_language_en)
            if active_language_en
            else Language.objects.get(en_label="English")  # default in English
        )

        # Get the instrument label in the active language
        # Set label to the first instrument name added in the language if there is no "umil_label" set
        active_labels = instrument_names.filter(language=context["active_language"])
        umil_label = active_labels.filter(umil_label=True)
        if umil_label.exists():
            context["active_instrument_label"] = umil_label.first()
        else:
            context["active_instrument_label"] = active_labels.first()

        # Get all languages for the dropdown
        context["languages"] = Language.objects.all()

        context["active_tab"] = "instruments"

        return context
