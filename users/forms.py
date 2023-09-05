
from django.contrib.auth.forms import AuthenticationForm
from django import forms

from django.utils.translation import gettext_lazy as _


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Имя пользователя'), widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    password = forms.CharField(label=_('Введите пароль'),
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control'}
                               ))

