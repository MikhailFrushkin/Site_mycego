from collections import defaultdict
from datetime import timedelta, datetime
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F, Subquery, ExpressionWrapper, FloatField
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from loguru import logger

from completed_works.models import WorkRecord, WorkRecordQuantity
from users.models import CustomUser
from utils.utils import get_dates
from work_schedule.models import Appointment


def today_current():
    import datetime
    today = datetime.date.today()
    year = today.year
    week = today.isocalendar()[1]
    print(year, week)
    return year, week


class Effectiveness(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/effectiveness.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('effectiveness:effectiveness')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.get(pk=self.request.user.id)

        appointment_list = (Appointment.objects.filter(user=user, verified=True).
                            values_list('date', flat=True).distinct().order_by('date'))
        week_data = defaultdict(set)
        for date in appointment_list:
            year = date.year
            week = date.strftime('%U')
            week_data[year].add(week)

        full_dict = {}
        for year, weeks in week_data.items():
            user_works_dict = {}

            for week in weeks:
                user_work_dict = {}

                appointments_duration = Appointment.objects.filter(
                    user=user,
                    date__week=week
                ).aggregate(total_duration=Sum('duration'))

                total_seconds = appointments_duration['total_duration'].total_seconds()
                hours = int(total_seconds // 3600 or 0)

                user_records = WorkRecord.objects.filter(
                    user=user,
                    date__week=week,
                    is_checked=True
                )
                user_work_count = defaultdict(int)

                for record in user_records:
                    record_quantities = WorkRecordQuantity.objects.filter(work_record=record)
                    for quantity in record_quantities:
                        user_work_count[quantity.standard] += quantity.quantity

                user_work_dict['operations'] = {key: value for key, value in user_work_count.items() if value != 0}
                user_work_dict['hours'] = hours

                result = 0
                kf = 0
                for key, value in user_work_dict['operations'].items():
                    result += value / key.standard
                if result:
                    kf = 100 if result / (0.01 * hours) > 100 else result / (0.01 * hours)

                user_work_dict['kf'] = kf
                user_work_dict['salary'] = round((kf * user.role.salary * hours) / 100, 2)

                user_works_dict[week] = user_work_dict
            user_works_dict_sorted = dict(sorted(user_works_dict.items(), key=lambda item: item[0], reverse=True))
            full_dict[year] = user_works_dict_sorted
        # pprint(full_dict)
        context['full_dict'] = full_dict
        return context


class StatisticView(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/statistic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now()

        total_employees = CustomUser.objects.count()
        total_employees_work = CustomUser.objects.filter(status_work=True).count()
        context['total_employees'] = total_employees
        context['total_employees_work'] = total_employees_work
        context['active_employees'] = total_employees_work
        context['none_work'] = 0
        appointment_dates = (Appointment.objects.filter(verified=True)
                             .values_list('date', flat=True)
                             .distinct()
                             .order_by('date'))

        week_data = defaultdict(set)
        for date in appointment_dates:
            year = int(date.year)
            week = int(date.strftime('%U'))
            week_data[year].add(week)

        inactive_employees = []

        for user in CustomUser.objects.filter(status_work=True):
            closest_appointment = (Appointment.objects.filter(
                user=user,
                date__lt=current_date + timedelta(days=1)
            ).order_by('-date').first())

            closest_date = None
            days_difference = None

            if closest_appointment:
                closest_date = datetime.combine(closest_appointment.date, datetime.min.time())
                closest_date = timezone.make_aware(closest_date, timezone.get_current_timezone())
                days_difference = (current_date - closest_date).days
            else:
                context['none_work'] += 1
            if days_difference is None or days_difference >= 7:
                if days_difference is None:
                    pass
                else:
                    inactive_employees.append((user, closest_date, days_difference))

        context['inactive_employees'] = sorted(
            inactive_employees, key=lambda x: x[2], reverse=True)
        context['active_employees'] = context['active_employees'] - len(context['inactive_employees']) - context[
            'none_work']

        users = CustomUser.objects.all()
        past_date = current_date - timezone.timedelta(weeks=1)
        current_date = current_date - timezone.timedelta(days=1)
        missing_appointments_dict = {}
        missing_work_records_dict = {}

        # Итерируемся по каждому пользователю
        for user in users:
            # Находим даты, у которых есть записи в модели Appointment, но нет в модели WorkRecord для данного пользователя
            appointments_without_work_records = Appointment.objects.filter(
                user=user, date__range=(past_date, current_date)
            ).exclude(
                date__in=WorkRecord.objects.filter(user=user, date__range=(past_date, current_date)).values(
                    'date')
            )
            # Находим даты, у которых есть записи в модели WorkRecord, но нет в модели Appointment для данного пользователя
            work_records_without_appointments = WorkRecord.objects.filter(
                user=user, date__range=(past_date, current_date)
            ).exclude(
                date__in=Appointment.objects.filter(user=user, date__range=(past_date, current_date)).values(
                    'date')
            )

            # Заполняем словари для данного пользователя
            if len(appointments_without_work_records) > 0:
                for item in appointments_without_work_records:
                    if item.date in missing_appointments_dict:
                        missing_appointments_dict[item.date].append(item.user)
                    else:
                        missing_appointments_dict[item.date] = [item.user]

            if len(work_records_without_appointments) > 0:
                for item in work_records_without_appointments:
                    print(item)
                    if item.date in missing_work_records_dict:
                        missing_work_records_dict[item.date].append(item)
                    else:
                        missing_work_records_dict[item.date] = [item]

        context['missing_appointments_dict'] = dict(sorted(missing_appointments_dict.items(), key=lambda x: x[0]))

        context['missing_work_records_dict'] = dict(sorted(missing_work_records_dict.items(), key=lambda x: x[0]))

        very_good_works = {}
        work_records = WorkRecord.objects.filter(date__range=(past_date, current_date))

        for record in work_records:
            id = record.id
            date = record.date
            user = record.user
            total_hours = Appointment.objects.filter(user=user, date=date).aggregate(Sum('duration'))['duration__sum']
            if total_hours:
                total_hours = total_hours.total_seconds() / 3600
                works = WorkRecordQuantity.objects.filter(work_record=record)
                hours_work = 0
                for work in works:
                    if work.quantity > 0:
                        hours_work += work.quantity / work.standard.standard
                kf = round(hours_work / total_hours * 100, 2)
                if kf > 200:
                    if date in very_good_works:
                        very_good_works[date].append((record, kf))
                    else:
                        very_good_works[date] = [(record, kf)]
        context['very_good_works'] = very_good_works
        pprint(context['very_good_works'])

        return context
