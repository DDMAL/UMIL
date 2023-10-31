from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="main:home"),
        name="logout",
    ),
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/change_password.html",
            success_url="/",
        ),
        name="change_password",
    ),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
            redirect_field_name="next",
            next_page="main:home",
        ),
        name="login",
    ),
]
