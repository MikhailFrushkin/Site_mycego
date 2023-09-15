from collections import defaultdict
from datetime import timedelta, datetime
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F
from django.db.models import Q
from django.db.models.functions import ExtractWeekDay, ExtractHour
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from completed_works.models import WorkRecord, WorkRecordQuantity
from users.models import CustomUser
from work_schedule.models import Appointment


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

        # 1. сколько работников за время было
        context['total_employees'] = CustomUser.objects.count()
        # сколько работников работает
        context['total_employees_work'] = CustomUser.objects.filter(status_work=True).count()

        # 2. сколько активных работников сейчас
        active_employees = CustomUser.objects.filter(
            Q(appointment__date__gte=current_date - timedelta(days=7)) | Q(appointment__date__isnull=True),
            status_work=True
        ).distinct().count()
        context['active_employees'] = active_employees

        # 3. Список неактивных сотрудников
        inactive_employees = CustomUser.objects.filter(
            Q(appointment__date__lt=current_date - timedelta(days=7)) & Q(status_work=True)
        ).distinct()
        context['inactive_employees'] = inactive_employees

        appointment_list = (Appointment.objects.filter(verified=True).
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

                users = Appointment.objects.filter(verified=True).values_list('user', flat=True).distinct().order_by(
                    'user')
                for user_id in users:
                    user = get_object_or_404(CustomUser, pk=user_id)
                    appointments_duration = Appointment.objects.filter(
                        user=user,
                        date__week=week
                    ).aggregate(total_duration=Sum('duration'), total_day=Count('date'))
                    if appointments_duration['total_duration']:
                        temp_dict = {
                            'hours': 0,
                            'average_hours': 0,
                            'days_without_work': 0,
                        }
                        total_seconds = appointments_duration['total_duration'].total_seconds()
                        hours = int(total_seconds // 3600 or 0)
                        temp_dict['hours'] = hours

                        days = appointments_duration['total_day']
                        temp_dict['average_hours'] = int(hours / days)

                        closest_appointment = Appointment.objects.filter(
                            user=user,
                            date__lt=current_date
                        ).order_by('-date').first()
                        if closest_appointment:
                            closest_date = datetime.combine(closest_appointment.date,
                                                            datetime.min.time())  # Convert to datetime
                            closest_date = timezone.make_aware(closest_date, timezone.get_current_timezone())
                            days_difference = (current_date - closest_date).days
                        else:
                            closest_date = None
                            days_difference = None
                        temp_dict['days_without_work'] = (closest_date, days_difference)

                        user_work_dict[user] = temp_dict

                user_works_dict[week] = user_work_dict
            full_dict[year] = user_works_dict
        context['full_dict'] = full_dict
        # pprint(context)
        return context
