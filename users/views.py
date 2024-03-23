from collections import OrderedDict
from datetime import datetime
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from completed_works.models import WorkRecord, WorkRecordQuantity
from pay_sheet.models import PaySheetModel
from users.forms import UserLoginForm, CustomUserEditForm, UserProfileEditForm
from users.models import CustomUser, Role
from work_schedule.models import Appointment


class UserLogin(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'
    redirect_authenticated_user = 'main_site:main_site'

    def form_valid(self, form):
        # Проверяем work_status пользователя
        user = form.get_user()
        if user.status_work:
            return super().form_valid(form)
        else:
            # Если work_status равно False, перенаправляем пользователя обратно на страницу входа
            return HttpResponseRedirect(reverse_lazy('users:login'))


class UserLogout(LogoutView):
    template_name = 'user/login.html'


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser  # Замените на вашу модель профиля пользователя
    form_class = UserProfileEditForm  # Замените на вашу форму обновления профиля
    template_name = 'user/edit_profile.html'  # Замените на ваш шаблон обновления профиля
    success_url = reverse_lazy('users:user_profile')  # URL, на который перейдет пользователь после успешного обновления

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def get_success_url(self):
        # Получаем user_id текущего пользователя
        user_id = self.request.user.id
        # Генерируем URL с передачей user_id
        return reverse_lazy('users:user_profile', kwargs={'user_id': user_id})


class Staff(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user/staff.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('users:staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cashed_data = cache.get('staff', None)
        if cashed_data:
            return cashed_data

        # # Желаемые роли, которые должны идти впереди
        # desired_roles = ['Директор',
        #                  'Директор по производству',
        #                  'Администратор сайта',
        #                  'Руководитель сервисного отдела',
        #                  'Сервисный инженер',
        #                  'Сервисный инженер (стажер)',
        #                  'Руководитель',
        #                  'Руководитель склада',
        #                  'Руководитель 3д наклеек, наклеек на карту',
        #                  'Руководитель отдела Постеров, боксов, попсокетов',
        #                  'Руководитель отдела значков',
        #                  'Руководитель отдела FBO',
        #                  'Руководитель отдела кружек',
        #                  'Тренер',
        #                  'Печатник',
        #                  'Маркировщик',
        #                  'Фасовщик пакетов на упаковке',
        #                  ]

        # Создаем упорядоченный словарь для хранения данных
        staff_by_role = OrderedDict()
        desired_roles = Role.objects.order_by('order_by')
        # Добавляем выбранные роли и соответствующие им пользователи
        for role in desired_roles:
            users_with_role = CustomUser.objects.filter(role=role, status_work=True).order_by('-avg_kf')
            if users_with_role.count() > 0:
                staff_by_role[role] = list(users_with_role)

        context['staff_by_role'] = staff_by_role

        context.pop('view', None)
        cache.set('staff', context, 30)
        return context


def user_profile(request, user_id):
    profile = get_object_or_404(CustomUser, pk=user_id)
    pay_sheets = PaySheetModel.objects.filter(user=profile)
    work_lists = WorkRecord.objects.filter(user=profile, delivery=None)

    work_summary = {}
    if len(work_lists) > 0:
        for work_record in work_lists:
            work_quantities = WorkRecordQuantity.objects.filter(work_record=work_record)

            for work_quantity in work_quantities:
                if work_quantity.standard:
                    work_type = work_quantity.standard.name
                else:
                    work_type = 'Удаленный вид работ'
                quantity = work_quantity.quantity
                if work_type in work_summary:
                    work_summary[work_type] += quantity
                else:
                    work_summary[work_type] = quantity

    sorted_work_summary = dict(sorted(work_summary.items(), key=lambda item: item[1], reverse=True))

    summary_data = {
        'total_hours': 0,
        'total_result_salary': 0,
        'total_bonus': 0,
        'total_penalty': 0,
    }

    for pay_sheet in pay_sheets:
        summary_data['total_hours'] += pay_sheet.hours
        summary_data['total_result_salary'] += pay_sheet.result_salary
        summary_data['total_bonus'] += pay_sheet.bonus
        summary_data['total_penalty'] += pay_sheet.penalty

    context = {
        'profile': profile,
        'work_summary': sorted_work_summary,
        'summary_data': summary_data
    }
    pprint(context)
    return render(request, 'user/user_profile.html', context)
