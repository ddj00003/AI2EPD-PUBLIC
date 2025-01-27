from django import forms
from django.utils.translation import gettext_lazy as _

class Login(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=100, required= True)
    password = forms.CharField(label=_('Contraseña'), max_length=100, required= True, widget=forms.PasswordInput)