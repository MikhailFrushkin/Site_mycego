from datetime import time

import factory
from django.utils import timezone
from faker import Faker
from users.models import CustomUser, Role
from work_schedule.models import Appointment

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
            self.role = RoleFactory()


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    user = factory.SubFactory(CustomUserFactory)
    date = fake.date_between(start_date='-1y', end_date='now')
    start_time = time(9, 0)  # 9 утра
    end_time = time(21, 0)   # 9 вечера
    verified = False


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Faker('user_name')
    salary = 150
