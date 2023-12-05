from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger

from users.models import CustomUser


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


class DeliveryState(models.Model):
    TYPE_CHOICES = [
        ('Значки', 'Значки'),
        ('Постеры', 'Постеры'),
    ]
    TYPE_CHOICES2 = [
        ('В листах', 'В листах'),
        ('В кол-во арт.', 'В кол-во арт.'),
        ('В шт.', 'В шт.'),
    ]
    name = models.CharField(verbose_name='Название этапа', max_length=100)
    number = models.IntegerField(verbose_name='Номер этапа')
    num_emp = models.IntegerField(verbose_name='Кол-во человек', default=1)
    standard = models.ForeignKey(Standards, on_delete=models.SET_NULL, verbose_name='Вид работ', blank=True, null=True)
    type = models.CharField(
        verbose_name='Тип',
        max_length=20,
        choices=TYPE_CHOICES,
        default='Значки'
    )
    type_quantity = models.CharField(
        verbose_name='В чем измеряется',
        max_length=20,
        choices=TYPE_CHOICES2,
        default='В шт.'
    )

    def __str__(self):
        return self.name


class Delivery(models.Model):
    id_wb = models.CharField(verbose_name='Идентификатор поставки', max_length=100)
    name = models.CharField(verbose_name='Наименование поставки', max_length=100)
    createdAt = models.DateTimeField(verbose_name='Дата создания поставки', null=True, blank=True)
    closedAt = models.DateTimeField(verbose_name='Дата закрытия поставки', null=True, blank=True)
    scanDt = models.DateTimeField(verbose_name='Дата скана поставки', null=True, blank=True)
    done = models.BooleanField(verbose_name='Флаг закрытия поставки', null=True, blank=True)
    products_count = models.IntegerField(verbose_name='Количество товаров', null=True, blank=True)
    lists = models.IntegerField(verbose_name='Количество листов', null=True, blank=True)
    products = models.JSONField(verbose_name='Артикулы товаров', blank=True, null=True)
    products_nums_on_list = models.JSONField(verbose_name='Номера на листах', blank=True, null=True, default=dict)
    price = models.IntegerField(verbose_name='Цена', blank=True, null=True)
    type = models.CharField(verbose_name='Апи', null=True, max_length=100)
    type_d = models.CharField(verbose_name='Тип товаров', null=True, max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    state = models.ForeignKey(DeliveryState, on_delete=models.PROTECT, verbose_name='Этап поставки', blank=True,
                              null=True)
    machin = models.CharField(verbose_name='Компьютер', null=True, max_length=100)

    def save(self, *args, **kwargs):
        super(Delivery, self).save(*args, **kwargs)
        if self.products_nums_on_list:
            try:
                self.machin = self.products_nums_on_list.get('1').get('comp')
                super(Delivery, self).save(*args, **kwargs)
            except Exception as ex:
                logger.error(ex)
            if DeliveryNums.objects.filter(delivery=self).count() == 0:
                if self.type_d == "badges":
                    delivery_states = DeliveryState.objects.filter(type="Значки").order_by('number')
                else:
                    delivery_states = DeliveryState.objects.filter(type="Постеры").order_by('number')
                for state in delivery_states:
                    try:
                        DeliveryNums.objects.create(delivery=self, state=state)
                    except Exception as ex:
                        logger.error(ex)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"


class DeliveryNums(models.Model):
    delivery = models.ForeignKey(Delivery, verbose_name='Поставка', on_delete=models.CASCADE)
    state = models.ForeignKey(DeliveryState, on_delete=models.CASCADE, verbose_name='Этап поставки', blank=True,
                              null=True)
    available_numbers = models.JSONField(verbose_name='Доступные числа', default=list, blank=True, null=True)
    not_available_numbers = models.JSONField(verbose_name='Не доступные числа', default=list, blank=True, null=True)
    ready_numbers = models.JSONField(verbose_name='Готовые числа', default=list, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(verbose_name='Готово', null=True, blank=True, default=False)

    def are_lists_equal(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        return set1 == set2

    def save(self, *args, **kwargs):
        if self.delivery.products_count:
            all_nums = list(range(1, len(self.delivery.products_nums_on_list) + 1))
            if self.state and self.state.name == 'Печать':
                self.available_numbers = all_nums
            self.available_numbers = [x for x in all_nums if
                                      x not in self.ready_numbers and x not in self.not_available_numbers]

            self.not_available_numbers = [x for x in all_nums if
                                          x not in self.available_numbers and x not in self.ready_numbers]

            self.status = self.are_lists_equal(all_nums, self.ready_numbers)

        super(DeliveryNums, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - {self.delivery.name}"


class DeliveryWorks(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='statuses')
    state = models.ForeignKey(DeliveryState, on_delete=models.SET_NULL, null=True, verbose_name='Этап поставки')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    quantity = models.IntegerField(verbose_name='Количество', blank=True, null=True)
    nums = models.JSONField(verbose_name='Сделаные номера', default=list, blank=True, null=True)
    comments = models.TextField(verbose_name='Комментарии', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.state} - {self.delivery.name}"


class WorkRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    hours = models.IntegerField(verbose_name='Кол-во часов', default=0)
    date = models.DateField(verbose_name='Дата')
    is_checked = models.BooleanField(verbose_name='Проверено', default=False)
    works = models.ManyToManyField(Standards, verbose_name='Виды работ', blank=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, verbose_name='Поставка', null=True, blank=True)
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

# @receiver(post_save, sender=Delivery)
# def create_delivery_nums(sender, instance, created, **kwargs):
#     if created:
#         if len(instance.products_nums_on_list) == 0:
#             logger.error(instance)
#             return
#         logger.success(instance)
#         if instance.type_d == "badges":
#             delivery_states = DeliveryState.objects.filter(type="Значки").order_by('number')
#         else:
#             delivery_states = DeliveryState.objects.filter(type="Постеры").order_by('number')
#
#         for state in delivery_states:
#             DeliveryNums.objects.create(delivery=instance, state=state)
