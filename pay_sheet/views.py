import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from loguru import logger

from completed_works.models import WorkRecord, WorkRecordQuantity, Standards
from users.models import CustomUser
from utils.utils import get_year_week, get_dates
from work_schedule.models import Appointment


class PaySheet(LoginRequiredMixin, TemplateView):
    template_name = 'pay_sheet/pay_sheet.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('pay_sheet:pay_sheet')

    # def create_excel_file(self, queryset, week):
    #     workbook = Workbook()
    #     worksheet = workbook.active
    #     worksheet.title = 'Записи на работу'
    #
    #     # Получите модель 'Appointment' из вашего приложения
    #     appointment_model = apps.get_model(app_label='work_schedule', model_name='Appointment')
    #
    #     # Получите метаданные модели, чтобы получить поля
    #     model_fields = appointment_model._meta.fields
    #
    #     # Добавьте столбец "Role" к заголовкам столбцов
    #     headers = [field.verbose_name for field in model_fields]
    #     headers.append('Должность')
    #
    #     # Создайте заголовки столбцов на основе полей модели
    #     for col_num, header in enumerate(headers, 1):
    #         worksheet.cell(row=1, column=col_num, value=header)
    #
    #     # Заполните данные из queryset
    #     for row_num, appointment in enumerate(queryset, 2):
    #         for col_num, field in enumerate(model_fields, 1):
    #             cell_value = getattr(appointment, field.name)
    #
    #             # Получите должность пользователя и добавьте ее в конец строки
    #             if field.name == 'user' and isinstance(cell_value, CustomUser):
    #                 worksheet.cell(row=row_num, column=col_num, value=cell_value.username)
    #                 worksheet.cell(row=row_num, column=len(headers), value=cell_value.role.name)
    #             else:
    #                 worksheet.cell(row=row_num, column=col_num, value=cell_value)
    #
    #             max_length = len(str(cell_value))
    #             column_letter = get_column_letter(col_num)
    #             if worksheet.column_dimensions[column_letter].width is None or worksheet.column_dimensions[
    #                 column_letter].width < max_length:
    #                 worksheet.column_dimensions[column_letter].width = max_length
    #
    #     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #     response['Content-Disposition'] = f'attachment; filename={week} week.xlsx'
    #     workbook.save(response)
    #
    #     return response
    #
    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     if 'download_excel' in request.GET:
    #         try:
    #             year = self.request.GET.get('year', None)
    #             week = self.request.GET.get('week', None)
    #             if not year or not week:
    #                 today = datetime.date.today()
    #                 year = today.year
    #                 week = today.isocalendar()[1]
    #
    #             queryset = Appointment.objects.filter(
    #                 date__year=year,
    #                 date__week=week
    #             )
    #         except:
    #             pass
    #
    #         excel_response = self.create_excel_file(queryset, week)
    #         return excel_response
    #
    #     context = self.get_context_data()
    #     return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_staff:
            raise Http404
        time_start = datetime.datetime.now()
        users_dict = {}
        total_salary = 0
        total_result_salary = 0

        # user = get_object_or_404(CustomUser, id=self.request.user.id)

        year = self.request.GET.get('year', None)
        week = self.request.GET.get('week', None)
        if not year or not week:
            today = datetime.date.today()
            year = today.year
            week = today.isocalendar()[1]
        else:
            year, week = int(year), int(week)
        monday, sunday = get_dates(year, week)
        for user in CustomUser.objects.all():
            queryset_appointments = Appointment.objects.filter(user=user, date__year=year, date__week=week,
                                                               verified=True)

            week_hours_work = []
            for i in range(7):
                date_day = monday + datetime.timedelta(days=i)
                try:
                    duration_day = sum([int(i.duration.total_seconds() / 3600) for i in
                                        queryset_appointments.filter(user=user, date=date_day)])
                    week_hours_work.append(duration_day)
                except Exception as ex:
                    print(ex)
                    week_hours_work.append(0)

            users_dict[user] = {'week_hours_work': week_hours_work}
            users_dict[user]['hours'] = sum(users_dict[user]['week_hours_work'])
            count_of_12 = users_dict[user]['week_hours_work'].count(12)
            users_dict[user]['count_of_12'] = count_of_12

            users_dict[user]['flag'] = True if count_of_12 >= 3 else False


            # Высчитывание зарплаты по часам
            salary = 0
            mess = ''

            if user.role.name == 'Упаковщик 2':
                if users_dict[user]['flag']:
                    for day_hour in users_dict[user]['week_hours_work']:
                        if day_hour == 12:
                            salary += 12 * 150
                        else:
                            salary += day_hour * 120
                else:
                    salary = sum([day_hour * 120 for day_hour in users_dict[user]['week_hours_work']])
                    mess = 'Не отработано 3 дня по 12ч.'
            else:
                salary = sum([day_hour * user.role.salary for day_hour in users_dict[user]['week_hours_work']])

            users_dict[user]['salary'] = salary
            total_salary += salary
            # высчитывание коэффецента к зарплате
            try:
                work_totals_dict = calculate_work_totals_for_week(user, users_dict[user]['hours'], monday, sunday)
                if work_totals_dict:
                    users_dict[user]['works'] = work_totals_dict
                    kf = sum([i[1] for i in work_totals_dict.values()]) * 100
                    users_dict[user]['kf'] = round(kf, 2)

                    if users_dict[user]['hours'] < 20 and user.role.name == 'Упаковщик':
                        result_salary = 0
                        mess = 'Отработанно меньше 20 часов'
                    elif kf >= 80:
                        result_salary = salary
                    else:
                        result_salary = round(salary * kf / 100, 2)
                        mess = 'Коэффецент меньше 80%'

                    users_dict[user]['result_salary'] = result_salary
                    total_result_salary += result_salary
                else:
                    users_dict[user]['works'] = {}
                    users_dict[user]['kf'] = 0
                    users_dict[user]['result_salary'] = 0
                    mess = 'Не работал'
                    if user.status_work == False:
                        mess = 'Уволен'
            except Exception as ex:
                pass
            users_dict[user]['comment'] = mess
        sorted_dict = dict(sorted(users_dict.items(), key=lambda x: str(x[0])))
        context['users_dict'] = sorted_dict

        timedelta_tuples = Appointment.objects.filter(date__week=week, verified=True).values_list('duration')
        timedelta_list = [item[0] for item in timedelta_tuples]
        total_hours = int(sum([i.total_seconds() for i in timedelta_list]) // 3600)
        context['total_hours'] = total_hours
        context['total_salary'] = total_salary
        context['total_result_salary'] = total_result_salary

        context['year'], context['week'] = get_year_week(self.request.GET, 'salary')
        context['monday'], context['sunday'] = monday, sunday
        # pprint(context)
        logger.success(datetime.datetime.now() - time_start)
        return context


def calculate_work_totals_for_week(user, hours, week_start_date, week_end_date):
    # Получите все записи работы за заданный период
    work_records = WorkRecord.objects.filter(user=user, date__range=(week_start_date, week_end_date), is_checked=True)

    # Используйте агрегацию, чтобы вычислить сумму работы для каждого вида работы
    work_totals = WorkRecordQuantity.objects.filter(work_record__in=work_records).values('standard').annotate(
        total_quantity=Sum('quantity'))

    # Создайте словарь, в котором ключами будут объекты модели Standards, а значениями - суммарное количество работы
    work_totals_dict = {}
    if work_totals:
        for work_total in work_totals:
            standard_id = work_total['standard']
            total_quantity = work_total['total_quantity']
            if total_quantity > 0:
                standard = Standards.objects.get(pk=standard_id)
                work_totals_dict[standard] = (total_quantity, total_quantity / (hours * standard.standard))

    return work_totals_dict
