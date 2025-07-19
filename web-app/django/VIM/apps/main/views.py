from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from django.db.models import Count
import json


def home(request):
    # Fetch statistics from database
    total_instruments = Instrument.objects.count()
    total_languages = Language.objects.count()
    total_names = InstrumentName.objects.count()
    total_editors = User.objects.count()

    # Chart data: Top 5 instruments with most languages
    top_instruments_by_languages = (
        Instrument.objects.annotate(
            language_count=Count("instrumentname__language", distinct=True)
        )
        .filter(language_count__gt=0)  # Only instruments with at least one language
        .order_by("-language_count")[:5]
    )

    instruments_chart_data = []
    for instrument in top_instruments_by_languages:
        # Get the English name if available, otherwise use the first available name
        try:
            english_name = instrument.instrumentname_set.filter(
                language__en_label="English"
            ).first()
            name = (
                english_name.name
                if english_name
                else instrument.instrumentname_set.first().name
            )
        except:
            name = f"Instrument {instrument.wikidata_id}"

        instruments_chart_data.append(
            {"name": name, "count": instrument.language_count}
        )

    # Chart data: Top 5 languages with most instrument names
    top_languages_by_names = (
        Language.objects.annotate(
            instrument_count=Count("instrumentname", distinct=True)
        )
        .filter(
            instrument_count__gt=0
        )  # Only languages with at least one instrument name
        .order_by("-instrument_count")[:5]
    )

    languages_chart_data = []
    for language in top_languages_by_names:
        languages_chart_data.append(
            {"name": language.en_label, "count": language.instrument_count}
        )

    context = {
        "active_tab": "home",
        "total_instruments": total_instruments,
        "total_languages": total_languages,
        "total_names": total_names,
        "total_editors": total_editors,
        "instruments_chart_data": json.dumps(instruments_chart_data),
        "languages_chart_data": json.dumps(languages_chart_data),
    }
    return render(request, "main/index.html", context)


def about(request):
    return render(request, "main/about.html", {"active_tab": "about"})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Add success parameter to the redirect URL for Google Analytics event tracking
            success_url = f"{reverse('main:home')}?registration=success"
            return redirect(success_url)
    else:
        form = UserCreationForm()

    return render(request, "main/registration/register.html", {"form": form})
