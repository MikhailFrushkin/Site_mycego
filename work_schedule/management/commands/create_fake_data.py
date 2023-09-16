from django.core.management.base import BaseCommand

from django.utils import timezone
from datetime import date

from work_schedule.factories import CustomUserFactory, AppointmentFactory


class Command(BaseCommand):
    help = 'Fill the database with fake data'

    def handle(self, *args, **kwargs):
        # Создайте 100 пользователей и записей на работу
        for _ in range(100):
            user = CustomUserFactory()
            appointment_date = date(2023, 9, 20)
            AppointmentFactory(user=user, date=appointment_date,
                               start_time=timezone.make_aware(timezone.datetime(2000, 1, 1, 9, 0)),
                               end_time=timezone.make_aware(timezone.datetime(2000, 1, 1, 21, 0)))

        self.stdout.write(self.style.SUCCESS('Successfully filled the database with fake data.'))
