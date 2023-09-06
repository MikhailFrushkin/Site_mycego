from datetime import datetime, date, timedelta
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from work_schedule.forms import AppointmentForm
from work_schedule.models import Appointment


def format_duration(duration):
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}"


def ajax_view(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date', None)
        print(selected_date)

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
                                  "verified": appointment.verified} for appointment in appointments]
        else:
            appointments_list = [{"user": 'пусто', "date": 'пусто',
                                  "start_time": 'пусто',
                                  "end_time": 'пусто',
                                  "duration": 'пусто',
                                  "verified": 'пусто'}]
        response_data = {'appointments': appointments_list}
        # pprint(response_data)
        return JsonResponse(response_data)


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
