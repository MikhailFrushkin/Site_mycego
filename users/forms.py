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
        fields = ('username', 'email', 'role')


class CustomUserChangeForm(UserChangeForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Выберите должность")
    status_work = forms.BooleanField(label='Работает', initial=True, required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'status_work', 'photo', 'phone_number',
            'telegram_id', 'card_details', 'birth_date', 'hobbies'
        )


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'status_work', 'photo', 'phone_number', 'telegram_id',
                  'card_details', 'birth_date', 'hobbies']

    def __init__(self, *args, **kwargs):
        super(CustomUserEditForm, self).__init__(*args, **kwargs)
        # Можно добавить кастомные атрибуты или стили для полей формы здесь, если нужно


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'photo', 'phone_number', 'telegram_id', 'card_details',
                  'birth_date', 'hobbies']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Добавьте здесь дополнительные проверки, если необходимо
        return phone_number

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data['telegram_id']
        # Добавьте здесь дополнительные проверки, если необходимо
        return telegram_id

    def clean_card_details(self):
        card_details = self.cleaned_data['card_details']
        # Добавьте здесь дополнительные проверки, если необходимо
        return card_details
