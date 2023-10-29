from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
                   widget=forms.TextInput(attrs={'class': 'form-control'}), 
                   label="Username"
               )
    password = forms.CharField(
                   widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
                   label="Password"
               )