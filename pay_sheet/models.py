from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from users.models import CustomUser


class PaySheetModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год')
    week = models.IntegerField(verbose_name='Неделя')

    role = models.CharField(verbose_name='Должность', max_length=50)
    role_salary = models.CharField(verbose_name='Ставка', max_length=10)
    hours = models.DecimalField(verbose_name='Часы', max_digits=10, decimal_places=2)
    salary = models.DecimalField(verbose_name='Зарплата по ставке', max_digits=10, decimal_places=2)
    works = models.TextField(verbose_name='Выполненые работы')
    count_of_12 = models.IntegerField(verbose_name='Отработанно дней по 12 часов')
    kf = models.DecimalField(verbose_name='Коэффицент', max_digits=10, decimal_places=2)
    result_salary = models.DecimalField(verbose_name='Итоговая зарплата', max_digits=10, decimal_places=2)
    bonus = models.IntegerField(verbose_name='Премия')
    penalty = models.IntegerField(verbose_name='Штраф')
    comment = models.TextField(verbose_name='Комментарий')

    created_at = models.DateTimeField(verbose_name='Созданно', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновленно', auto_now=True)

    class Meta:
        ordering = ['year', 'week']
        verbose_name = "Расчетный лист"
        verbose_name_plural = "Расчетные листы"

    def __str__(self):
        return f'{self.user}-{self.year}_{self.week}'


class PaySheetMonthModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год')
    month = models.IntegerField(verbose_name='Месяц')

    role = models.CharField(verbose_name='Должность', max_length=50)
    role_salary = models.CharField(verbose_name='Ставка', max_length=10)
    hours = models.DecimalField(verbose_name='Часы', max_digits=10, decimal_places=2)
    salary = models.DecimalField(verbose_name='Зарплата по ставке', max_digits=10, decimal_places=2)
    works = models.TextField(verbose_name='Выполненые работы')
    count_of_12 = models.IntegerField(verbose_name='Отработанно дней по 12 часов')
    kf = models.DecimalField(verbose_name='Коэффицент', max_digits=10, decimal_places=2)
    result_salary = models.DecimalField(verbose_name='Итоговая зарплата', max_digits=10, decimal_places=2)
    bonus = models.IntegerField(verbose_name='Премия')
    penalty = models.IntegerField(verbose_name='Штраф')
    comment = models.TextField(verbose_name='Комментарий')

    created_at = models.DateTimeField(verbose_name='Созданно', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновленно', auto_now=True)

    class Meta:
        ordering = ['year', 'month']
        verbose_name = "Расчетный лист(месяц)"
        verbose_name_plural = "Расчетные листы(месяц)"

    def __str__(self):
        return f'{self.user}-{self.year}_{self.month}'


@receiver(pre_save, sender=PaySheetModel)
def validate_result_salary(sender, instance, **kwargs):
    if instance.result_salary < 0:
        instance.comment = f"штраф больше зп на {abs(instance.result_salary)}"
        instance.result_salary = 0
