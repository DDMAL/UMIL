import json
import re

from django.http import Http404
from django.views.generic import DetailView
from VIM.apps.instruments.models import Instrument, Language, HornbostelSachs


class InstrumentDetail(DetailView):
    """
    Displays details of a specific instrument.
    """

    model = Instrument
    template_name = "instruments/detail.html"
    context_object_name = "instrument"
    slug_field = "umil_id"
    slug_url_kwarg = "umil_id"

    def get_object(self, queryset=None):
        """
        Override to validate UMIL ID format before database lookup.

        Valid format: UMIL-##### (e.g., UMIL-00001, UMIL-12345)
        """
        umil_id = self.kwargs.get("umil_id")

        # Validate UMIL ID format: UMIL- followed by exactly 5 digits
        if not re.match(r"^UMIL-\d{5}$", umil_id):
            raise Http404(f"Invalid UMIL ID format: {umil_id}")

        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = context["instrument"]

        # Query the instrument names in all languages
        instrument_names = instrument.instrumentname_set.all().select_related(
            "language"
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
        context["languages"] = json.dumps(
            list(
                Language.objects.values(
                    "wikidata_code",
                    "autonym",
                    "en_label",
                    "html_direction",
                )
            )
        )

        context["active_tab"] = "instruments"

        # Determine if the current user can delete the instrument
        context["can_delete_instrument"] = (
            self.request.user.is_authenticated
            and context["instrument"].is_user_created
            and (
                self.request.user.is_superuser
                or context["instrument"].created_by == self.request.user
            )
        )
        # Add user HBS to the context, if present
        user_hbs = None
        user = self.request.user
        if user.is_authenticated:
            user_hbs_qs = HornbostelSachs.objects.filter(
                instrument=instrument, contributor=user
            ).order_by(
                "-is_main", "-id"
            )  # prioritize main if more than one, fallback to latest
            if user_hbs_qs.exists():
                user_hbs = user_hbs_qs.first()
        context["user_hbs"] = user_hbs

        # Add HBS proposals for this instrument to the context, if instrument has no HBS
        if not instrument.hornbostel_sachs_class:
            hbs_proposals_qs = (
                HornbostelSachs.objects.filter(instrument=instrument, is_main=False)
                .order_by("-id")
                .values_list("hbs_class", flat=True)
            )
            # Deduplicate and sort
            hbs_proposals = sorted(set(hbs_proposals_qs))
            context["hbs_proposals"] = hbs_proposals
        else:
            context["hbs_proposals"] = None

        return context
