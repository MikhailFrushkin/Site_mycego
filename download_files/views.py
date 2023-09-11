from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from download_files.forms import UploadExcelForm
from users.models import CustomUser, Role
from work_schedule.models import Appointment
import pandas as pd


class DownloadFiles(LoginRequiredMixin, FormView):
    template_name = 'download/download.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('download:download')
    form_class = UploadExcelForm

    def form_valid(self, form):
        excel_file = form.cleaned_data['excel_file']
        print(excel_file)
        try:
            # Используйте Pandas для чтения файла Excel
            df = pd.read_excel(excel_file, engine='openpyxl')
            print(df.columns)
            for index, row in df.iterrows():
                username = row['username']
                first_name = row['first_name']
                last_name = row['last_name']
                role_name = row['role_name']
                password = row['password']

                # Проверяем, существует ли пользователь по username
                user, created = CustomUser.objects.get_or_create(username=username)

                # Обновляем поля пользователя
                user.first_name = first_name
                user.last_name = last_name
                user.set_password(password)

                # Находим или создаем роль
                role, created = Role.objects.get_or_create(name=role_name)

                user.role = role
                user.save()

        except Exception as e:
            return render(self.request, self.template_name, {'form': form, 'error_message': str(e)})

        return super().form_valid(form)