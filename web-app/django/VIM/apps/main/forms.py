from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, 
    UserCreationForm, 
    PasswordChangeForm,
)
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = User
        fields = ("username", "password")


class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="Email Address", required=True)
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True
    )
    password2 = forms.CharField(
        label="Password Confirmation", widget=forms.PasswordInput, required=True
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")
