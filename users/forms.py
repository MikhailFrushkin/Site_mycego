from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Role
from django.utils.translation import gettext_lazy as _


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Имя пользователя'), widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    password = forms.CharField(label=_('Введите пароль'),
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control'}
                               ))


class CustomUserCreationForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Выберите должность")
    status_work = forms.BooleanField(label='Работает', initial=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'status_work')


class CustomUserChangeForm(UserChangeForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Выберите должность")
    status_work = forms.BooleanField(label='Работает', initial=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'status_work')