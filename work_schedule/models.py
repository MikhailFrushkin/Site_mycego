from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField(verbose_name='Начало работы')
    end_time = models.TimeField(verbose_name='Конец работы')
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    duration = models.DurationField(blank=True, null=True, verbose_name='Продолжительность')
    verified = models.BooleanField(default=False, verbose_name='Проверено')

    class Meta:
        ordering = ['date']
        verbose_name = "Заявка на работу"
        verbose_name_plural = "Заявки на работу"

    def save(self, *args, **kwargs):
        # Вычисляем разницу между start_time и end_time
        if self.start_time and self.end_time:
            start_datetime = timezone.make_aware(
                timezone.datetime(2000, 1, 1, self.start_time.hour, self.start_time.minute))
            end_datetime = timezone.make_aware(timezone.datetime(2000, 1, 1, self.end_time.hour, self.end_time.minute))
            self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)


class Role(models.Model):
    name = models.CharField(verbose_name='Должность', max_length=255)
    salary = models.IntegerField(verbose_name='Ставка', default=0)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    days = models.IntegerField(verbose_name='Дней для заявки в график', default=14)

    def __str__(self):
        return self.user.username