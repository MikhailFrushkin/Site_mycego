from django.db import models

from users.models import CustomUser


class Delivery(models.Model):
    id_wb = models.CharField(verbose_name='Идентификатор поставки', max_length=100)
    name = models.CharField(verbose_name='Наименование поставки', max_length=100)
    createdAt = models.DateTimeField(verbose_name='Дата создания поставки', null=True)
    closedAt = models.DateTimeField(verbose_name='Дата закрытия поставки', null=True)
    scanDt = models.DateTimeField(verbose_name='Дата скана поставки', null=True)
    done = models.BooleanField(verbose_name='Флаг закрытия поставки', null=True)
    products_count = models.IntegerField(verbose_name='Количество товаров')
    products = models.JSONField(verbose_name='Артикулы товаров', blank=True, null=True)
    price = models.IntegerField(verbose_name='Цена')
    type = models.CharField(verbose_name='Апи', null=True, max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"


class Standards(models.Model):
    name = models.CharField(verbose_name='Тип работ', max_length=255)
    standard = models.IntegerField(verbose_name='Норматив', default=0)
    type_for_printer = models.BooleanField(verbose_name='Относиться к печатникам', default=False, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид работы"
        verbose_name_plural = "Виды работ"


class WorkRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    hours = models.IntegerField(verbose_name='Кол-во часов', default=0)
    date = models.DateField(verbose_name='Дата')
    is_checked = models.BooleanField(verbose_name='Проверено', default=False)
    works = models.ManyToManyField(Standards, verbose_name='Виды работ', blank=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, verbose_name='Поставка', null=True)

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
