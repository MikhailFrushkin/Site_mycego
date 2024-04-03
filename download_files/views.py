from datetime import datetime
from pprint import pprint

import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from loguru import logger

from completed_works.models import WorkRecordQuantity
from download_files.forms import UploadExcelForm
from users.models import CustomUser, Role
from utils.utils import df_in_xlsx
from work_schedule.models import FingerPrint


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None


class DownloadFiles(LoginRequiredMixin, FormView):
    template_name = 'download/download.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('main_site:main_site')
    form_class = UploadExcelForm

    def form_valid(self, form):
        excel_files = [
            form.cleaned_data['excel_file'],
            form.cleaned_data['excel_file2'],
        ]

        if excel_files[0]:
            try:
                bad_users = []
                file_name = excel_files[0]
                df = pd.read_excel(file_name, sheet_name='ПАЛЬЧИКИ')
                df['username'] = df['Фамилия'] + '_' + df['Имя']
                df['username'] = df['username'].apply(lambda x: x.strip())
                users_list = zip(df['username'].tolist(), df['никнейм'].tolist())
                for i in users_list:
                    try:
                        user = CustomUser.objects.get(username=i[0])
                        user.nick = i[1]
                        user.save()
                    except Exception as ex:
                        logger.error(i[0])
                        logger.error(ex)
                        bad_users.append(i[0])
                if bad_users:
                    messages.error(self.request, f'Не найденные имена на сайте {bad_users}')
                with open('Не найденные ники в базе.txt', 'w') as f:
                    f.write('\n'.join(bad_users))
            except Exception as ex:
                logger.debug(ex)
        if excel_files[1]:
            not_user_in_db = []
            date_format = "%Y/%m/%d %H:%M:%S"
            df = pd.DataFrame()
            try:
                file_name = excel_files[1]
                df = pd.read_csv(file_name, delimiter='\t')
                df['DateTime'] = df['DateTime'].apply(lambda x: datetime.strptime(x, date_format))
                df['Date'] = df['DateTime'].dt.date
                df['Time'] = df['DateTime'].dt.time
                # df_in_xlsx(df, 'После обработки')
            except Exception as ex:
                logger.debug(ex)

            for index, row in df.iterrows():
                try:
                    user = get_or_none(CustomUser, nick=row['Name'])
                    if user is not None:
                        temp, _ = FingerPrint.objects.get_or_create(
                            user=user,
                            EnNo=row['EnNo'],
                            date=row['Date'],
                            time=row['Time'],
                        )
                    else:
                        not_user_in_db.append(str(row['Name']))
                except Exception as ex:
                    with open('Ошибки при запси отпечаток.txt', 'a') as f:
                        f.write(f"{ex} {row['Name']}\n")
            mes = ', '.join(set(not_user_in_db))
            if mes:
                messages.error(self.request, f'Не найденные имена на сайте {mes}')
            with open('Нет таких ников в базе сайта.txt', 'w') as f:
                f.write(mes)

        return super().form_valid(form)


class DownloadUser(LoginRequiredMixin, FormView):
    template_name = 'download/download_user.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('main_site:main_site')
    form_class = UploadExcelForm

    def form_valid(self, form):
        excel_file = form.cleaned_data['excel_file']
        logger.info(excel_file)
        try:
            # Используйте Pandas для чтения файла Excel
            df = pd.read_excel(excel_file, engine='openpyxl')
            for index, row in df.iterrows():
                username = row['Ник']
                first_name = row['Имя']
                last_name = row['Фамилия']
                role_name = row['Должность']
                email = row['Почта']
                if isinstance(row['Телефон'], str):
                    phone_number = row['Телефон']
                else:
                    phone_number = str(row['Телефон']).split('.')[0]
                password = row['Пароль']
                status_work = True
                logger.info(username)
                logger.info(first_name)
                logger.info(last_name)
                logger.info(role_name)
                logger.info(email)
                logger.info(phone_number)
                logger.info(password)
                try:
                    # Находим или создаем роль
                    role, created = Role.objects.get_or_create(name=role_name)

                    user, created = CustomUser.objects.get_or_create(username=username)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.phone_number = phone_number
                    user.status_work = status_work
                    if email:
                        user.email = email
                    logger.success(user)
                    user.set_password(password)
                    user.role = role
                    user.save()

                except Exception as ex:
                    logger.error(ex)

        except Exception as ex:
            logger.error(ex)
            return render(self.request, self.template_name, {'form': form, 'error_message': str(ex)})

        return super().form_valid(form)

