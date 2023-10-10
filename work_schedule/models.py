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




class FingerPrint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник',
                             related_name='fingerprints')
    EnNo = models.IntegerField(verbose_name='ID')
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Запись со сканера"
        verbose_name_plural = "Записи со сканера"


class BadFingerPrint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    date = models.DateField(verbose_name='Дата')
    comment = models.TextField(verbose_name='Косяк')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Косяк"
        verbose_name_plural = "Косяки"


class VacationRequest(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_checked = models.BooleanField(default=False)
    duration = models.PositiveIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        # При сохранении объекта вычисляем продолжительность и обновляем поле duration
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.duration = delta.days + 1  # Прибавляем 1, чтобы включить начальную и конечную даты
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заявка на отпуск от {self.employee.username}"

    class Meta:
        verbose_name = 'Заявка на отпуск'
        verbose_name_plural = 'Заявки на отпуск'



