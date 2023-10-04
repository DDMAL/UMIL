from django.shortcuts import render


def home(request):
    return render(request, "main/index.html", {"active_tab": "home"})


def about(request):
    return render(request, "main/about.html", {"active_tab": "about"})
