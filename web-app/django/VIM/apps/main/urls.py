from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from VIM.apps.main.forms import EmailAuthenticationForm

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path(
        "verify-email-pending/", views.verify_email_pending, name="verify_email_pending"
    ),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path(
        "resend-verification/",
        views.resend_verification_email,
        name="resend_verification",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="main:home"),
        name="logout",
    ),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="main/auth/changePassword.html",
            success_url="/",
        ),
        name="change_password",
    ),
    path("accounts/login/", views.custom_login, name="login"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="main/auth/resetPassword.html",
            email_template_name="main/auth/resetPasswordEmail.html",
            success_url="/password-reset/done/",
        ),
        name="reset_password",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="main/auth/resetPasswordDone.html",
        ),
        name="reset_password_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="main/auth/resetPasswordConfirm.html",
            success_url="/reset-password-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="main/auth/resetPasswordComplete.html",
        ),
        name="password_reset_complete",
    ),
]
