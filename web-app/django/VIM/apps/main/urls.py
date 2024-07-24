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
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/changePassword.html",
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
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/resetPassword.html",
            email_template_name="registration/resetPasswordEmail.html",
            success_url="/password-reset/done/",
        ),
        name="reset_password",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/resetPasswordDone.html",
        ),
        name="reset_password_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/resetPasswordConfirm.html",
            success_url="/reset-password-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/resetPasswordComplete.html",
        ),
        name="password_reset_complete",
    ),
]
