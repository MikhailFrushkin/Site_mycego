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

    def __str__(self):
        return self.username