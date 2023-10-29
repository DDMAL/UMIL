from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("login/", views.login_view, name="login"),
    path("change_password/", views.change_password, name="change_password"),
    path("logout/", views.user_logout, name="logout"),
]
