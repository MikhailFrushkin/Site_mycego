import json
from collections import defaultdict
from datetime import timedelta, datetime
from pprint import pprint

from django.core.cache import cache
from django.db.models import Min, Max, Count
from django.db.models.functions import ExtractWeek, ExtractYear
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from loguru import logger

from completed_works.models import WorkRecord, WorkRecordQuantity, Standards
from users.models import CustomUser, Role
from work_schedule.models import Appointment


def today_current():
    import datetime
    today = datetime.date.today()
    year = today.year
    week = today.isocalendar()[1]
    return year, week


class StatisticViewBad(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/statistic_bad.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cashed_data = cache.get('context_bad', None)
        if cashed_data:
            return cashed_data
        start_time = datetime.now()

        current_date = timezone.now()
        users = CustomUser.objects.filter(status_work=True)

        total_employees = CustomUser.objects.count()
        total_employees_work = CustomUser.objects.filter(status_work=True).count()
        context['total_employees'] = total_employees
        context['total_employees_work'] = total_employees_work
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
        none_work_users = Appointment.objects.all().values('user_id')
        unique_user_ids = total_employees - len(set([item['user_id'] for item in none_work_users]))

        for user in users:
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
            if days_difference is None or days_difference >= 7:
                if days_difference is None:
                    pass
                else:
                    inactive_employees.append((user, closest_date, days_difference))

        context['inactive_employees'] = sorted(
            inactive_employees, key=lambda x: x[2], reverse=True)

        context['active_employees'] = total_employees - len(context['inactive_employees']) - unique_user_ids

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
                date__in=WorkRecord.objects.filter(user=user, date__range=(past_date, current_date),
                                                   delivery=None).values(
                    'date')
            )
            # Находим даты, у которых есть записи в модели WorkRecord, но нет в модели Appointment для данного пользователя
            work_records_without_appointments = WorkRecord.objects.filter(
                user=user, delivery=None, date__range=(past_date, current_date)
            ).exclude(
                date__in=Appointment.objects.filter(user=user, date__range=(past_date, current_date)).values(
                    'date')
            )

            # Заполняем словари для данного пользователя
            if appointments_without_work_records:
                for item in appointments_without_work_records:
                    if item.date in missing_appointments_dict:
                        missing_appointments_dict[item.date].append(item.user)
                    else:
                        missing_appointments_dict[item.date] = [item.user]

            if work_records_without_appointments:
                for item in work_records_without_appointments:
                    if item.date in missing_work_records_dict:
                        missing_work_records_dict[item.date].append(item)
                    else:
                        missing_work_records_dict[item.date] = [item]

        context['missing_appointments_dict'] = dict(sorted(missing_appointments_dict.items(), key=lambda x: x[0]))

        context['missing_work_records_dict'] = dict(sorted(missing_work_records_dict.items(), key=lambda x: x[0]))

        very_good_works = {}
        work_records = WorkRecord.objects.filter(date__range=(past_date, current_date), delivery=None)

        for record in work_records:
            date = record.date
            user = record.user
            total_hours = Appointment.objects.filter(user=user, date=date).aggregate(Sum('duration'))['duration__sum']
            if total_hours:
                total_hours = total_hours.total_seconds() / 3600
                works = WorkRecordQuantity.objects.filter(work_record=record)
                hours_work = 0
                for work in works:
                    if work.quantity > 0 and work.standard:
                        hours_work += work.quantity / work.standard.standard
                kf = round(hours_work / total_hours * 100, 2)
                if kf > 200:
                    if date in very_good_works:
                        very_good_works[date].append((record, kf))
                    else:
                        very_good_works[date] = [(record, kf)]
        context['very_good_works'] = very_good_works
        context.pop('view', None)
        cache.set('context_bad', context, 600)
        logger.success(datetime.now() - start_time)

        return context


class StatisticWorks(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/statistic_emp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cashed_data = cache.get('context_works', None)
        if cashed_data:
            return cashed_data
        start_time = datetime.now()

        current_date = datetime.today().date()
        start_date = current_date - timedelta(days=7)

        users = CustomUser.objects.filter(status_work=True)
        results = {}

        appointments = {}
        for appointment in Appointment.objects.filter(user__in=users, date__range=(start_date, current_date)):
            if appointment.user_id not in appointments:
                appointments[appointment.user_id] = {}
            exec_row = appointments[appointment.user_id].get(appointment.date, None)
            if exec_row:
                appointments[appointment.user_id][appointment.date] += appointment.duration.total_seconds() / 3600
            else:
                appointments[appointment.user_id][appointment.date] = appointment.duration.total_seconds() / 3600
        user_data_dict = {}

        for user in users:
            user_records = WorkRecordQuantity.objects.filter(
                work_record__user=user,
                work_record__delivery=None,
                work_record__date__gte=start_date
            ).order_by('work_record__user', 'work_record__date').values('work_record__id', 'work_record__date',
                                                                        'standard__name').annotate(
                total_quantity=Sum(F('quantity') * 1.0),
                total_standard=Sum(F('standard__standard') * 1.0)
            ).annotate(
                result=ExpressionWrapper(
                    F('total_quantity') / F('total_standard'),
                    output_field=FloatField()
                )
            )
            if user_records:
                user_total_quantity = {}
                for record in user_records:
                    date = record['work_record__date']
                    record_id = record['work_record__id']
                    result = record['result']
                    hours = appointments.get(user.id, {}).get(date, None)
                    if not hours:
                        continue
                    if date not in user_total_quantity:
                        user_total_quantity[date] = [0, record_id]
                    if result:
                        user_total_quantity[date][0] += round((result / hours) * 100, 2)
                if user_total_quantity:
                    user_data_dict[user] = user_total_quantity
                    if len(user_total_quantity) >= 2:
                        results[user] = user_total_quantity

        avg_kf_dict = {
            'bad': [],
            'medium': [],
            'good': [],
        }
        for user, data in user_data_dict.items():
            avg_value = round(sum(item[0] for item in data.values()) / len(data), 2)
            if avg_value < 80:
                avg_kf_dict['bad'].append((user, avg_value))
            elif 80 <= avg_value < 100:
                avg_kf_dict['medium'].append((user, avg_value))
            elif avg_value >= 100:
                avg_kf_dict['good'].append((user, avg_value))
            else:
                avg_kf_dict['bad'].append((user, 'Ошибка'))
        for key in avg_kf_dict:
            avg_kf_dict[key] = sorted(avg_kf_dict[key], key=lambda x: x[1])

        context["avg_kf_dict"] = avg_kf_dict

        filtered_results = {}
        for user, user_data in results.items():
            prev_date = None
            prev_value = None
            for date, value in user_data.items():
                if prev_date is not None and abs(value[0] - prev_value[0]) > 40:
                    if user not in filtered_results:
                        filtered_results[user] = {}
                    delta = round((value[0] - prev_value[0]), 2)
                    filtered_results[user][date] = value, delta
                    if prev_date not in filtered_results[user]:
                        filtered_results[user][prev_date] = prev_value, 0
                prev_date = date
                prev_value = value
        sorted_data = {user: dict(sorted(user_data.items())) for user, user_data in filtered_results.items()}
        rounded_data = {
            user: {
                date: ([round(val[0][0], 2), round(val[0][1], 2)], val[1])
                for date, val in user_data.items()
            }
            for user, user_data in sorted_data.items()
        }
        context['filtered_results'] = rounded_data

        context.pop('view', None)
        cache.set('context_works', context, 600)
        logger.success(datetime.now() - start_time)
        return context


class StatisticKfUsers(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/statistic_kf_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cashed_data = cache.get('context_kf', None)
        if cashed_data:
            return cashed_data
        start_time = datetime.now()
        current_datetime = timezone.now()
        current_year = current_datetime.year
        current_week_number = current_datetime.isocalendar()[1]
        standards = Standards.objects.all()
        # Создаем словарь для хранения данных
        data_dict = {}
        role_user = ['Фасовщик пакетов на упаковке', 'Маркировщик', 'Печатник', 'Упаковщик', 'Упаковщик 2']
        # Аннотируем данные с группировкой по году и вычисляем минимальную и максимальную неделю
        year_week_data = WorkRecord.objects.filter(user__role__name__in=role_user).annotate(
            year=ExtractYear('date'),
            week=ExtractWeek('date'),
            user_role=F('user__role__name')  # Аннотация должности сотрудника
        ).values('year', 'week', 'user_role').order_by('user_role', 'year', 'week')

        for data in year_week_data:
            year = data['year']
            week = data['week']
            if current_year == year and current_week_number == week:
                continue
            user_role = data['user_role']
            total_work_hours = 0

            # Get or create the nested dictionaries for year, week, and user_role
            user_role_dict = data_dict.setdefault(user_role, {})
            year_dict = user_role_dict.setdefault(year, {})
            week_dict = year_dict.setdefault(week, {})

            # Query WorkRecord for the current year, week, and user_role
            work_records = WorkRecord.objects.filter(
                date__year=year,
                date__week=week,
                user__role__name=user_role,
                delivery=None
            )
            work_records_q = (WorkRecordQuantity.objects.filter(work_record__in=work_records)
                              .filter(standard__in=standards)
                              .values('standard__name', 'standard__standard')
                              .annotate(total_quantity=Sum('quantity')))

            for item in work_records_q:
                total_work_hours += round(item['total_quantity'] / item['standard__standard'], 2)

            for i in standards:
                for j in work_records_q:
                    if j['standard__name'] == i.name:
                        week_dict[j['standard__name']] = [j['total_quantity'], 0, 0]
                if i.name not in week_dict:
                    week_dict[i.name] = [0, 0, 0]

            appointment_user_role = Appointment.objects.filter(
                date__year=year,
                date__week=week,
                user__role__name=user_role
            ).values('duration').aggregate(Sum('duration'))['duration__sum']

            week_dict['Кол-во листов работ'] = [work_records.count(), 0, 0]
            week_dict['Общее время'] = [
                round(appointment_user_role.total_seconds() // 3600, 2) if appointment_user_role else 0, 0, 0]
            week_dict['Общий кф'] = [round(total_work_hours * 100 / week_dict['Общее время'][0], 2) if week_dict[
                'Общее время'][0] else 0, 0, 0]

        changes = calculate_weekly_changes(data_dict)
        # pprint(changes)
        context['data'] = changes
        context.pop('view', None)
        cache.set('context_kf', context, 3600)
        with open(f"json.json", "w") as f:
            json.dump(changes, f, indent=4, ensure_ascii=False)

        logger.success(datetime.now() - start_time)
        return context


def calculate_weekly_changes(data):
    for worker, years in data.items():
        for year, weeks in years.items():
            prev_week = None
            for week, stats in weeks.items():
                if prev_week:
                    for work, quantity in stats.items():
                        data[worker][year][week][work][1] = round(quantity[0] - prev_week[work][0], 2)
                        if prev_week[work][0]:
                            data[worker][year][week][work][2] = round(
                                (quantity[0] - prev_week[work][0]) * 100 / prev_week[work][0], 2)

                prev_week = stats

    return data


class MainStatisticMenu(LoginRequiredMixin, TemplateView):
    template_name = 'effectiveness/statistic_main.html'
