from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm, CustomPasswordChangeForm


def home(request):
    return render(request, "main/index.html", {"active_tab": "home"})


def about(request):
    return render(request, "main/about.html", {"active_tab": "about"})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("main:home")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("main:home")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("main:home")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("main:home")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "registration/change_password.html", {"form": form})
