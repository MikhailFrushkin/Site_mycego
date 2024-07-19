from collections import OrderedDict
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from loguru import logger

from completed_works.models import WorkRecord, WorkRecordQuantity
from pay_sheet.models import PaySheetModel, PaySheetMonthModel
from users.forms import UserLoginForm, UserProfileEditForm
from users.models import CustomUser, Department


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
    template_name = 'user/staff.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('users:staff')

    def get_queryset(self):
        departments = Department.objects.all()

        # Sort the departments based on the length of their parent_departments list
        departments = sorted(departments, key=lambda d: len(d.get_all_parent_departments()))

        # for department in departments:
        #     parent_departments = department.get_all_parent_departments()
        #     logger.info(department)
        #     logger.info(parent_departments)
        return departments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        departments = self.object_list
        user_dict = OrderedDict()
        for department in departments:
            department_name = department.name if department.name else "Не указан отдел"
            head_of_department = department.head.all()
            # Получение всех пользователей, кроме руководителей отделов
            users = CustomUser.objects.filter(status_work=True, department=department).exclude(
                id__in=head_of_department.values_list('id', flat=True)).order_by('-avg_kf')
            if users or head_of_department:
                user_dict[department_name] = (head_of_department, users)

        not_dep = CustomUser.objects.filter(status_work=True, department__isnull=True).order_by('-avg_kf')
        context['user_dict'] = user_dict
        context['not_dep'] = not_dep
        return context


@login_required(login_url='/users/login/')
def user_profile(request, user_id):
    profile = get_object_or_404(CustomUser, pk=user_id)
    pay_sheets_week = PaySheetModel.objects.filter(user=profile)
    pay_sheets_month = PaySheetMonthModel.objects.filter(user=profile)
    pay_sheets = list(pay_sheets_month) + list(pay_sheets_week)
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
    return render(request, 'user/user_profile.html', context)


def toggle_favorite(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    current_user = request.user
    if current_user.is_authenticated:
        if user in current_user.favorites.all():
            current_user.favorites.remove(user)
            is_favorite = False
        else:
            current_user.favorites.add(user)
            is_favorite = True
        return JsonResponse({'is_favorite': is_favorite})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)
