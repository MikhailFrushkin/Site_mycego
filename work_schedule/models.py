from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Appointment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
        conflicting_appointments = Appointment.objects.filter(
            user=self.user,
            date=self.date,
        ).exclude(pk=self.pk)  # Исключите текущую запись, чтобы избежать сравнения с самой собой

        # Проверьте каждую запись на пересечение
        for appointment in conflicting_appointments:
            if self.start_time < appointment.end_time and self.end_time > appointment.start_time:
                # Если есть пересечение, уменьшите время конца предыдущей записи
                appointment.end_time = self.start_time
                appointment.save()

        # Вычислите продолжительность и сохраните запись
        start_datetime = timezone.make_aware(
            timezone.datetime(2000, 1, 1, self.start_time.hour, self.start_time.minute))
        end_datetime = timezone.make_aware(timezone.datetime(2000, 1, 1, self.end_time.hour, self.end_time.minute))
        self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)