from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class EmailUserCreationForm(UserCreationForm):
    username = forms.EmailField(
        label="Email",
        required=True,
        help_text="Required. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )
