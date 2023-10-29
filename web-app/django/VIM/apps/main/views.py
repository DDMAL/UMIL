from django.contrib.auth import login, update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from .forms import LoginForm


def home(request):
    return render(request, "main/index.html", {"active_tab": "home"})


def about(request):
    return render(request, "main/about.html", {"active_tab": "about"})


def login_view(request):
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


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Important for keeping the user authenticated
            return redirect("main:home")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/change_password.html", {"form": form})
