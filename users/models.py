from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    TYPE_SALARY = [
        ('Нет', 'Нет'),
        ('Раз в неделю', 'Раз в неделю'),
        ('Раз в месяц', 'Раз в месяц'),
    ]
    TYPE_SALARY2 = [
        ('Почасовая', 'Почасовая'),
        ('Оклад', 'Оклад'),
    ]
    name = models.CharField(verbose_name='Должность', max_length=255)
    salary = models.IntegerField(verbose_name='Ставка', default=0)
    type_salary = models.CharField(
        verbose_name='Выплаты',
        max_length=20,
        choices=TYPE_SALARY,
        default='Раз в неделю'
    )
    type_salary2 = models.CharField(
        verbose_name='Расчет зп',
        max_length=20,
        choices=TYPE_SALARY2,
        default='Почасовая'
    )
    calc_kf = models.BooleanField(verbose_name='Расчет коэффецента эффективности', default=True)
    works_standards = models.ManyToManyField('completed_works.Standards', verbose_name='Виды работ',
                                             blank=True)
    order_by = models.IntegerField(verbose_name='Порядок', default=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey("users.Department", on_delete=models.SET_NULL, null=True)
    favorites = models.ManyToManyField('self', symmetrical=False, related_name='favorited_by', blank=True)

    status_work = models.BooleanField(default=True, blank=True)
    photo = models.ImageField(verbose_name='Фото', upload_to='user_photos', blank=True, null=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=15, blank=True)
    telegram_id = models.CharField(verbose_name='Телеграмм', max_length=255, blank=True)
    card_details = models.CharField(verbose_name='Реквизиты карты', max_length=255, blank=True)
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    hobbies = models.CharField(verbose_name='Увлечения', max_length=255, blank=True)
    nick = models.CharField(verbose_name='Никнейм отпечатков', max_length=100, blank=True, default='')
    avg_kf = models.FloatField(verbose_name='Средная эффективность', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.first_name:
            if self.last_name:
                return f'{self.last_name} {self.first_name}'
            return f'{self.first_name}'
        return self.username


class Department(models.Model):
    name = models.CharField(verbose_name='Отдел', max_length=255)
    parent_department = models.ForeignKey(
        'self',
        verbose_name='Вышестоящий отдел',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subdepartments'
    )
    head = models.ManyToManyField(
        "users.CustomUser",
        verbose_name='Руководитель отдела',
        blank=True,
        related_name='head_of_department'
    )

    @classmethod
    def get_or_none(cls, **kwargs):
        """Получает объект или возвращает None, если не найден."""
        try:
            return cls.objects.get(**kwargs)
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return self.name

    def get_all_parent_departments(self, parent_departments=None):
        if parent_departments is None:
            parent_departments = []

        if self.parent_department:
            parent_departments.append(self.parent_department)
            self.parent_department.get_all_parent_departments(parent_departments)

        return parent_departments

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"


class DepartmentWorks(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отдел')
    works = models.ManyToManyField('completed_works.Standards', verbose_name='работы')

    def __str__(self):
        return self.department.name

    class Meta:
        verbose_name = "Работа отдела"
        verbose_name_plural = "Работы отдела"