from django.views.generic import DetailView
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from django.http import HttpResponseRedirect
from django.shortcuts import render
from ..forms.add_name_form import NameForm
from django.shortcuts import get_object_or_404

class InstrumentDetail(DetailView):
    """
    Displays details of a specific instrument.
    """

    model = Instrument
    template_name = "instruments/detail.html"
    context_object_name = "instrument"
    form_class = NameForm

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

        context["active_instrument_name"] = (context["instrument_names"].filter(
            language=context["active_language"]))

        context["languages"] = Language.objects.all()

        context["form"] = NameForm(
            initial={
                "instrument": context["instrument"].wikidata_id
            }
        )
        return context
    
    def post(self, request, **kwargs):
        instrument = get_object_or_404(Instrument, pk=kwargs.get("pk"))
        form = NameForm(request.POST)
        if form.is_valid():
            language_code = form.cleaned_data["language"]
            entry = {
                "name": form.cleaned_data["name"],
                "source": form.cleaned_data["source_name"],
            }
            # Save instrument name into database
            # If the instrument already has a name in specified language, save as alias
            if instrument.instrumentname_set.filter(language=language_code).exists():
                InstrumentName.objects.create(
                instrument=instrument,
                language=language_code,
                name=entry["name"],
                source_name=entry["source"],
                is_alias= True,
                contributor=request.user,
            )
            # If the instrument does not have a name in specified language, save as primary name    
            else:
                InstrumentName.objects.create(
                instrument=instrument,
                language=language_code,
                name=entry["name"],
                source_name=entry["source"],
                is_alias= False,
                contributor=request.user,
            )
            # Redirect to the instrument detail page
            return HttpResponseRedirect("/instrument/" + str(instrument.pk) + "/")

        return render(request, self.template_name, {"form": form})
