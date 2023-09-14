from django.db import models

from users.models import CustomUser


class Standards(models.Model):
    name = models.CharField(verbose_name='Тип работ', max_length=255)
    standard = models.IntegerField(verbose_name='Норматив', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид работы"
        verbose_name_plural = "Виды работ"


class WorkRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    date = models.DateField(verbose_name='Дата')
    is_checked = models.BooleanField(verbose_name='Проверено', default=False)
    works = models.ManyToManyField(Standards, verbose_name='Виды работ', blank=True)

    def __str__(self):
        return f"{self.user} - {self.date}"

    class Meta:
        verbose_name = "Запись работы"
        verbose_name_plural = "Записи работы"


class WorkRecordQuantity(models.Model):
    work_record = models.ForeignKey(WorkRecord, on_delete=models.CASCADE, verbose_name='Запись работы')
    standard = models.ForeignKey(Standards, on_delete=models.SET_NULL, verbose_name='Вид работы', null=True)
    quantity = models.IntegerField(verbose_name='Количество работы', default=0)

    def __str__(self):
        return f"{self.work_record} - {self.standard}"

    class Meta:
        verbose_name = "Количество работы"
        verbose_name_plural = "Количества работы"