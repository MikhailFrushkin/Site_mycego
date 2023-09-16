from django.test import TestCase
from .factories import CustomUserFactory, AppointmentFactory
from datetime import date

from .models import Appointment


class YourTestCase(TestCase):
    def test_create_users_and_appointments(self):
        # Создать 100 пользователей
        users = [CustomUserFactory() for _ in range(100)]

        # Создать 100 записей на работу на 20.09.2023 для первых 100 пользователей
        appointment_date = date(2023, 9, 20)
        for user in users[:100]:
            AppointmentFactory(user=user, date=appointment_date)

        # Теперь у вас есть 100 пользователей и 100 записей на работу на 20.09.2023.
        queryset = Appointment.objects.all()
        for i in queryset:
            print(
                i.user,
                i.date,
                i.start_time,
                i.end_time,
                i.duration,
                i.verified,
            )
        print(queryset.count())
