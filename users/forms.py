from io import BytesIO

from PIL import Image
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from loguru import logger

from .models import CustomUser, Role, Department
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
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Выберите отдел")
    status_work = forms.BooleanField(label='Работает', initial=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'department')


class CustomUserChangeForm(UserChangeForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Выберите должность")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Выберите отдел")
    status_work = forms.BooleanField(label='Работает', initial=True, required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'status_work', 'photo', 'phone_number',
            'telegram', 'card_details', 'birth_date', 'hobbies'
        )


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'status_work', 'photo', 'phone_number',
                  'telegram', 'card_details', 'birth_date', 'hobbies']

    def __init__(self, *args, **kwargs):
        super(CustomUserEditForm, self).__init__(*args, **kwargs)
        # Можно добавить кастомные атрибуты или стили для полей формы здесь, если нужно


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'photo', 'phone_number', 'telegram', 'card_details',
                  'birth_date', 'hobbies']

        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.birth_date:
            birth_date_str = self.instance.birth_date.strftime('%Y-%m-%d')
            self.initial['birth_date'] = birth_date_str

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            # Проверка расширения файла
            allowed_extensions = ['png', 'jpg', 'jpeg']
            extension = str(photo.name.split('.')[-1]).lower()

            if extension not in allowed_extensions:
                raise ValidationError('Пожалуйста, загрузите изображение в формате png, jpg или jpeg.')

            # Проверка размера изображения (не обязательная часть)
            max_size = (1024, 1024)  # Пример: максимальный размер 1024x1024
            image = Image.open(photo)

            # Поворот изображения, если оно в горизонтальной ориентации
            if hasattr(image, '_getexif'):  # Проверка наличия EXIF данных (для JPEG)
                exif = image._getexif()
                if exif and exif.get(0x0112):
                    orientation = exif.get(0x0112)
                    if orientation == 2:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        image = image.rotate(180)
                    elif orientation == 4:
                        image = image.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 5:
                        image = image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 6:
                        image = image.rotate(-90, expand=True)
                    elif orientation == 7:
                        image = image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
            else:  # Если нет EXIF данных, то проверяем размеры изображения
                width, height = image.size
                if width > height:
                    image = image.transpose(Image.ROTATE_270)

            image.thumbnail(max_size)
            output = BytesIO()
            image.save(output, format=image.format)
            output.seek(0)

            # Создание нового объекта ImageFieldFile и присвоение его полю photo
            photo = ImageFile(output, name=f"{self.instance.pk}_profile_picture.{extension}")

        return photo
