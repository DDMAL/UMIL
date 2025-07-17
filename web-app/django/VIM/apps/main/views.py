from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from VIM.apps.instruments.models import Instrument, Language


def home(request):
    # Fetch statistics from database
    total_instruments = Instrument.objects.count()
    total_languages = Language.objects.count()
    total_editors = User.objects.count()

    context = {
        "active_tab": "home",
        "total_instruments": total_instruments,
        "total_languages": total_languages,
        "total_editors": total_editors,
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
            return redirect("main:home")
    else:
        form = UserCreationForm()

    return render(request, "main/registration/register.html", {"form": form})
