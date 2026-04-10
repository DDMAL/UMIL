import json
import re

from django.http import Http404
from django.views.generic import DetailView
from VIM.apps.instruments.models import Instrument, Language
from django.db.models import Case, When, Value
from collections import defaultdict, OrderedDict


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

        # Get the active language from the session; fallback to English.
        active_language_en = self.request.session.get("active_language_en", "English")
        try:
            active_lang = Language.objects.get(en_label=active_language_en)
        except Language.DoesNotExist:
            active_lang = Language.objects.get(en_label="English")
        context["active_language"] = active_lang

        # Query the instrument names in all languages, sorted
        instrument_names = (
            context["instrument"]
            .instrumentname_set.all()
            .select_related("language")
            .annotate(
                active_lang_first=Case(
                    When(language=active_lang, then=Value(1)),
                    default=Value(0),
                )
            )
            .order_by(
                "-active_lang_first",  # active_lang matched names come first for display
                "-umil_label",
                "id",  # earlier created names come first
            )
        )

        # Determine label in the active language, prioritizing umil_label and earliest created
        active_label_qs = instrument_names.filter(language=active_lang, umil_label=True)
        if active_label_qs.exists():
            context["active_instrument_label"] = active_label_qs.earliest("id")
        elif instrument_names.filter(language=active_lang).exists():
            context["active_instrument_label"] = instrument_names.filter(
                language=active_lang
            ).earliest("id")
        else:
            context["active_instrument_label"] = ""

        # Control visibility of names: verified only for guests
        if self.request.user.is_authenticated:
            instrument_names_visible = instrument_names.all()
        else:
            instrument_names_visible = instrument_names.filter(
                verification_status="verified"
            )
        context["instrument_names"] = instrument_names_visible

        # Build names by language
        names_by_lang = defaultdict(list)
        for instrumentname in instrument_names:
            names_by_lang[instrumentname.language].append(instrumentname)

        # Build the language order: active first (if present), then all others by earliest InstrumentName creation
        lang_candidate_order = [
            lang for lang in names_by_lang.keys() if lang != active_lang
        ]
        # Sort non-active languages by the minimum id of their names
        lang_candidate_order.sort(
            key=lambda language: min(n.id for n in names_by_lang[language])
        )
        lang_order = [active_lang] if active_lang in names_by_lang else []
        lang_order.extend(lang_candidate_order)

        label_aliases_dict = OrderedDict()
        for language in lang_order:
            namelist = names_by_lang[language]
            label = None
            aliases = []

            # Find earliest umil_label for label
            umil_labels = [n for n in namelist if n.umil_label]
            if umil_labels:
                label = sorted(umil_labels, key=lambda n: n.id)[0]
                aliases = [n for n in namelist if n != label]
            else:
                # No umil_label, use earliest name as label
                ordered = sorted(namelist, key=lambda n: n.id)
                if ordered:
                    label = ordered[0]
                    aliases = ordered[1:]

            label_aliases_dict[language] = {"label": label, "aliases": aliases}

        context["label_aliases_dict"] = label_aliases_dict

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

        context["can_delete_instrument"] = (
            self.request.user.is_authenticated
            and context["instrument"].is_user_created
            and (
                self.request.user.is_superuser
                or context["instrument"].created_by == self.request.user
            )
        )

        return context
