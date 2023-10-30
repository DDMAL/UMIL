from django.contrib.auth import login
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm


def home(request):
    return render(request, "main/index.html", {"active_tab": "home"})


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

    return render(request, "registration/register.html", {"form": form})
