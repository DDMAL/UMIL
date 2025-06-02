from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from ..forms.add_name_form import NameForm
from VIM.apps.instruments.models import InstrumentName


class MyFormView(View):
    form_class = NameForm
    initial = {"key": "value"}
    template_name = "instruments/add_name.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            wikidata_id = form.cleaned_data["instrument"]
            language_code = form.cleaned_data["language"]
            entry = {
                "name": form.cleaned_data["name"],
                "source": form.cleaned_data["source_name"],
                "alias": form.cleaned_data["is_alias"],
            }
            # Here you would typically save the data to the database
            # For example:
            InstrumentName.objects.create(
                instrument=wikidata_id,
                language=language_code,
                name=entry["name"],
                source_name=entry["source"],
                is_alias=entry["alias"],
                contributor=request.user,
            )
            # Redirect to a success page or the instrument list
            return HttpResponseRedirect("/instruments/")

        return render(request, self.template_name, {"form": form})