import json
import locale
from datetime import date, timedelta, datetime, time
from pprint import pprint
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Case, When, Value
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import FormView, ListView
from loguru import logger

from users.models import CustomUser
from utils.utils import get_year_week
from work_schedule.forms import AppointmentForm
from work_schedule.models import Appointment


def format_duration(duration):
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}"


def ajax_view(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date', None)

        if selected_date == 'current_month':
            today = date.today()
            # Вычисление начальной даты текущего месяца
            start_date = date(today.year, today.month, 1)
            # Вычисление конечной даты текущего месяца
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1)
            else:
                end_date = date(today.year, today.month + 1, 1)
            appointments = Appointment.objects.filter(date__gte=start_date, date__lt=end_date)
        elif selected_date == 'all':
            appointments = Appointment.objects.all()
        elif selected_date == 'my':
            appointments = Appointment.objects.filter(user_id=request.user.id)
        else:
            appointments = Appointment.objects.filter(date=selected_date)

        if appointments:
            # Преобразуйте записи в список словарей
            appointments_list = [{"user": appointment.user.username, "date": appointment.date.strftime("%Y-%m-%d"),
                                  "start_time": appointment.start_time.strftime("%H:%M"),
                                  "end_time": appointment.end_time.strftime("%H:%M"),
                                  "duration": format_duration(appointment.duration),
                                  "verified": appointment.verified,
                                  "id": appointment.id,
                                  } for appointment in appointments]
        else:
            appointments_list = [{"user": 'пусто', "date": 'пусто',
                                  "start_time": 'пусто',
                                  "end_time": 'пусто',
                                  "duration": 'пусто',
                                  "verified": False,
                                  "id": 'пусто',
                                  }]
        response_data = {'appointments': appointments_list, 'user': request.user.username}
        return JsonResponse(response_data)


@login_required  # Ensure the user is logged in
@require_POST  # Accept only POST requests for this view
def delete_appointment(request):
    appointment_id = request.POST.get('id', None)
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.user == request.user:
        appointment.delete()  # Delete the appointment
        return JsonResponse({'message': 'Appointment deleted successfully.'})
    else:
        return JsonResponse({'message': 'You do not have permission to delete this appointment.'}, status=403)


@login_required
@require_POST
def update_appointment(request):
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        data_str = list(request.POST.keys())[0]
        data_dict = json.loads(data_str)

        date_str = data_dict.get('date')
        month_names = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }

        for month_name, month_number in month_names.items():
            if month_name in date_str:
                formatted_date_str = date_str.replace(month_name, str(month_number))
                date_obj = datetime.strptime(formatted_date_str, "%d %m %Y г.")
                break
        # Сначала удаляем старые записи
        Appointment.objects.filter(date=date_obj).delete()

        rowData = data_dict.get('rowData', [])
        for data in rowData:
            unique_elements = {}

            for index, item in enumerate(data):
                if item != 'Нет' and item != 'Очистить':
                    if item in unique_elements:
                        unique_elements[item].append(index)
                    else:
                        unique_elements[item] = [index]
            if unique_elements:
                for key, value in unique_elements.items():
                    value.sort()
                    grouped_values = []
                    current_group = [value[0]]
                    for i in range(1, len(value)):
                        if value[i] == value[i - 1] + 1:
                            current_group.append(value[i])
                        else:
                            grouped_values.append(current_group)
                            current_group = [value[i]]
                    grouped_values.append(current_group)

                    for group in grouped_values:
                        start_time = 9 + group[0]
                        if len(group) == 1:
                            end_time = 10 + group[0]
                        else:
                            end_time = 10 + group[-1]

                        start_time = time(start_time, 0)
                        end_time = time(end_time, 0)

                        appointment = Appointment(
                            user=CustomUser.objects.get(username=key),
                            date=date_obj,
                            start_time=start_time,
                            end_time=end_time,
                            verified=True,
                            comment=f"Утверждено в {datetime.now()}"
                        )
                        appointment.save()

        return JsonResponse({'message': 'Appointment update successfully.'})

    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)


class WorkSchedule(LoginRequiredMixin, FormView):
    template_name = 'work/work.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('work:work_page')
    form_class = AppointmentForm
    context_object_name = 'appointments'

    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.all()
        return self.render_to_response(self.get_context_data(form=self.get_form(), appointments=appointments))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']['user_id'] = self.request.user.id
        return kwargs

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = kwargs.get('appointments', [])
        return context

    def form_invalid(self, form):
        # Обработка случая, когда форма невалидна (возникли ошибки валидации)
        appointments = Appointment.objects.all()
        return self.render_to_response(self.get_context_data(form=form, appointments=appointments))


class EditWork(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'work/edit_work.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('work:edit_work')

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        year = self.request.GET.get('year')
        week = self.request.GET.get('week')
        if not year or not week:
            import datetime
            today = datetime.date.today()
            year = today.year
            week = today.isocalendar()[1] + 1

        queryset = Appointment.objects.filter(
            date__year=year,
            date__week=week
        )
        self._queryset = queryset  # Сохраняем результат в атрибуте _queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_start = datetime.now()
        queryset = self.get_queryset()

        unique_dates = queryset.values_list('date', flat=True).distinct()

        work_schedule = {}

        for index, date_appointment in enumerate(unique_dates):
            user_dict = {}
            appointments = queryset.filter(date=date_appointment).annotate(
                user_role=F('user__role__name')
            )
            # Задайте порядок сортировки с помощью функции Case
            appointments = appointments.annotate(
                custom_order=Case(
                    When(user_role="Руководитель", then=Value(1)),
                    When(user_role="Руководитель склада", then=Value(2)),
                    When(user_role="Сервисный инженер", then=Value(3)),
                    When(user_role="Печатник", then=Value(4)),
                    default=Value(5),  # Для всех остальных ролей
                    output_field=models.IntegerField(),
                )
            )

            # Теперь сортируйте результаты по полю 'custom_order', чтобы получить желаемый порядок
            appointments = appointments.order_by('custom_order')
            flag = True
            role_dict = {}
            for appointment in appointments:
                role = appointment.user.role
                if role:
                    if role not in role_dict:
                        role_dict[role] = 1
                    else:
                        role_dict[role] += 1

                if appointment.verified == False:
                    flag = False
                work_hours = [0] * 12
                start_hour = appointment.start_time.hour
                end_hour = appointment.end_time.hour
                for i in range(start_hour - 9, end_hour - 9):
                    work_hours[i] = 1  # Помечаем часы, когда пользователь работает
                if appointment.user in user_dict:
                    existing_work_hours = user_dict[appointment.user]
                    # Объединяем два списка с использованием логического ИЛИ
                    updated_work_hours = [a | b for a, b in zip(existing_work_hours, work_hours)]
                    # Обновляем запись в словаре
                    user_dict[appointment.user] = updated_work_hours
                else:
                    # Если записи нет, создаем новую
                    user_dict[appointment.user] = work_hours
            work_hours_count = {hour: sum([user_work_hours[hour] for user_work_hours in user_dict.values()]) for
                                hour in range(12)}
            work_schedule[(date_appointment, f'table-{index}')] = (user_dict, work_hours_count, flag, role_dict)

        context['work_schedule'] = work_schedule
        context['users'] = CustomUser.objects.filter(status_work=True).distinct().order_by('username')

        context['year'], context['week'] = get_year_week(self.request.GET)
        print(context['year'], context['week'])
        logger.success(datetime.now() - time_start)
        return context


class GrafUser(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'work/graf_user.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('work:graf_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(user=self.request.user, verified=True).order_by('date')
        context['appointments'] = appointments
        return context
