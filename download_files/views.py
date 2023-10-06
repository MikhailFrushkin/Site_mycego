import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from completed_works.models import WorkRecordQuantity
from download_files.forms import UploadExcelForm
from users.models import CustomUser, Role


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
                username = row['Ник']
                first_name = row['Имя']
                last_name = row['Фамилия']
                role_name = row['Должность']
                print(row['Телефон'])
                if isinstance(row['Телефон'], str):
                    phone_number = row['Телефон']
                else:
                    phone_number = str(row['Телефон']).split('.')[0]
                password = row['Пароль']
                status_work = row['Работа']
                print(phone_number)
                # Проверяем, существует ли пользователь по username
                user, created = CustomUser.objects.get_or_create(username=username)
                # Обновляем поля пользователя
                user.first_name = first_name
                user.last_name = last_name
                if status_work == 'Да':
                    user.status_work = True
                else:
                    user.status_work = False
                user.phone_number = phone_number
                user.set_password(password)

                # Находим или создаем роль
                role, created = Role.objects.get_or_create(name=role_name)

                user.role = role
                user.save()

        except Exception as e:
            return render(self.request, self.template_name, {'form': form, 'error_message': str(e)})

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        null_q = WorkRecordQuantity.objects.filter(quantity=0)
        null_q.delete()
        return context