from django.db import models

from users.models import CustomUser


class DeliveryStage(models.Model):
    name = models.CharField(verbose_name='Название этапа', max_length=100)
    number = models.IntegerField(verbose_name='Номер этапа', unique=True)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    id_wb = models.CharField(verbose_name='Идентификатор поставки', max_length=100)
    name = models.CharField(verbose_name='Наименование поставки', max_length=100)
    createdAt = models.DateTimeField(verbose_name='Дата создания поставки', null=True, blank=True)
    closedAt = models.DateTimeField(verbose_name='Дата закрытия поставки', null=True, blank=True)
    scanDt = models.DateTimeField(verbose_name='Дата скана поставки', null=True, blank=True)
    done = models.BooleanField(verbose_name='Флаг закрытия поставки', null=True, blank=True)
    products_count = models.IntegerField(verbose_name='Количество товаров', blank=True)
    products = models.JSONField(verbose_name='Артикулы товаров', blank=True, null=True)
    price = models.IntegerField(verbose_name='Цена', blank=True, null=True)
    type = models.CharField(verbose_name='Апи', null=True, max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    state = models.ForeignKey(DeliveryStage, on_delete=models.PROTECT, verbose_name='Этап поставки', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"


class DeliveryWorks(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='statuses')
    stage = models.ForeignKey(DeliveryStage, on_delete=models.SET_NULL, null=True, verbose_name='Этап поставки')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    quantity = models.IntegerField(verbose_name='Количество', blank=True, null=True)
    num_start = models.IntegerField(verbose_name='От', blank=True, null=True)
    num_end = models.IntegerField(verbose_name='До', blank=True, null=True)
    comments = models.TextField(verbose_name='Комментарии', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stage} - {self.delivery.name}"


class Standards(models.Model):
    name = models.CharField(verbose_name='Тип работ', max_length=255)
    standard = models.IntegerField(verbose_name='Норматив', default=0)
    type_for_printer = models.BooleanField(verbose_name='Относиться к печатникам', default=False)
    delivery = models.BooleanField(verbose_name='Отображать в листах поставки', default=False)

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
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)

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
