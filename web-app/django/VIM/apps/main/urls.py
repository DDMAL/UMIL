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
    path(
        "reset-password/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/reset_password.html",
            email_template_name="registration/reset_password_email.html",
            success_url="/reset-password-sent/",
        ),
        name="reset_password",
    ),
    path(
        "reset-password-sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/reset_password_sent.html",
        ),
        name="reset_password_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/reset_password_confirm.html",
            success_url="/reset-password-complete/",
        ),
        name="reset_password_confirm",
    ),
    path(
        "reset-password-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/reset_password_complete.html",
        ),
        name="reset_password_complete",
    ),
]
