from collections import OrderedDict
from datetime import datetime
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

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
    success_url = reverse_lazy('users:profile')  # URL, на который перейдет пользователь после успешного обновления

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class Staff(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user/staff.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('users:staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Желаемые роли, которые должны идти впереди
        desired_roles = ['Директор',
                         'Директор по производству',
                         'Администратор сайта',
                         'Руководитель',
                         'Руководитель склада',
                         'Сервисный инженер',
                         'Сервисный инженер (стажер)',
                         'Печатник']

        # Создаем упорядоченный словарь для хранения данных
        staff_by_role = OrderedDict()

        # Добавляем выбранные роли и соответствующие им пользователи
        for role_name in desired_roles:
            try:
                role = Role.objects.get(name=role_name)
                users_with_role = CustomUser.objects.filter(role=role).order_by('username')
                staff_by_role[role] = list(users_with_role)
            except:
                pass

        # Получаем остальные роли и добавляем их в словарь
        other_roles = Role.objects.exclude(name__in=desired_roles)
        for role in other_roles:
            users_with_role = CustomUser.objects.filter(role=role, status_work=True).order_by('username')
            if len(users_with_role) > 0:
                staff_by_role[role] = list(users_with_role)

        context['staff_by_role'] = staff_by_role
        return context


def user_profile(request, user_id):
    profile = get_object_or_404(CustomUser, pk=user_id)

    context = {
        'profile': profile,
    }

    return render(request, 'user/user_profile.html', context)
