import datetime
import os

import django

# Установите переменную окружения DJANGO_SETTINGS_MODULE на имя вашего settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mycego.settings")

# Инициализируйте Django
django.setup()

# Импортируйте фабрики и другие необходимые модули
from users.models import CustomUser, Role
from work_schedule.models import Appointment
from datetime import time
import factory
from faker import Faker

fake = Faker()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    status_work = True

    @factory.post_generation
    def role(self, create, extracted, **kwargs):
        if not create:
            # Пропустить, если фабрика не создает запись
            return

        if extracted:
            # Если role передается явно при создании объекта, используйте ее
            self.role = extracted
        else:
            # Иначе создайте случайную роль, используя RoleFactory
            self.role = Role.objects.all().order_by('?').first()


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    user = factory.SubFactory(CustomUserFactory)
    # Вычисляем начальную и конечную даты текущей недели

    # Создаем случайную дату на текущей неделе
    date = fake.date_between_dates(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=6))

    start_time = time(9, 0)  # 9 утра
    end_time = time(21, 0)  # 9 вечера
    verified = False


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Faker('user_name')
    salary = 150


if __name__ == '__main__':
    # custom_user = CustomUserFactory()
    for i in range(50):
        appointment = AppointmentFactory()
        # role = RoleFactory()
