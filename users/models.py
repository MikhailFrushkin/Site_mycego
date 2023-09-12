from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(verbose_name='Должность', max_length=255)
    salary = models.IntegerField(verbose_name='Ставка', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    status_work = models.BooleanField(default=True, blank=True)
    photo = models.ImageField(verbose_name='Фото', upload_to='user_photos', blank=True, null=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=15, blank=True)
    telegram_id = models.CharField(verbose_name='ID Телеграма', max_length=255, blank=True)
    card_details = models.CharField(verbose_name='Реквизиты карты', max_length=255, blank=True)
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    hobbies = models.TextField(verbose_name='Увлечения', blank=True)

    def __str__(self):
        return self.username


