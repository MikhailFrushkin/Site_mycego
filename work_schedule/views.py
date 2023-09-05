from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from work_schedule.forms import AppointmentForm
from work_schedule.models import Appointment


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
