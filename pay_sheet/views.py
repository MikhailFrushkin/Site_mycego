import datetime
import json
from pprint import pprint
import locale
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from loguru import logger

from completed_works.models import WorkRecord, WorkRecordQuantity, Standards
from pay_sheet.models import PaySheetModel
from users.models import CustomUser
from utils.utils import get_year_week, get_dates
from work_schedule.models import Appointment


class PaySheet(LoginRequiredMixin, TemplateView):
    template_name = 'pay_sheet/pay_sheet.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('pay_sheet:pay_sheet')

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

            try:
                row = PaySheetModel.objects.get(user=user, week=week, year=year)
                users_dict[user]['bonus'] = row.bonus
                users_dict[user]['penalty'] = row.penalty
            except:
                users_dict[user]['bonus'] = 0
                users_dict[user]['penalty'] = 0

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


@login_required
@require_POST
def created_salary_check(request):
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        data_str = list(request.POST.keys())[0]
        data_dict = json.loads(data_str)

        rowData = data_dict.get('rowData', [])
        year = data_dict.get('year')
        week = data_dict.get('week')
        clean_data = map(clean_data_post, rowData)
        dict_pays = {}
        for row in clean_data:
            try:

                user = CustomUser.objects.get(username=row[0])
                temp = {
                    'year': year,
                    'week': week,
                    'role': row[1],
                    'role_salary': row[2],
                    'hours': round(float(row[3]), 2) if row[3] != '' else 0,
                    'salary': round(float(row[4]), 2) if row[4] != '' else 0,
                    'works': row[5],
                    'count_of_12': int(row[6]) if row[6] != '' else 0,
                    'kf': round(float(row[7]), 2) if row[7] != '' else 0,
                    'result_salary': round(float(row[8]), 2) if row[8] != '' else 0,
                    'bonus': round(abs(float(row[9])), 2) if row[9] != '' else 0,
                    'penalty': round(abs(float(row[10])), 2) if row[10] != '' else 0,
                    'comment': row[11],
                }
                temp['result_salary'] = round(temp['result_salary'] + temp['bonus'] - temp['penalty'], 2)
                dict_pays[user] = temp
            except Exception as ex:
                print(ex)

        try:
            # Цикл для создания и сохранения объектов PaySheetModel
            for user, data in dict_pays.items():
                try:
                    # Проверяем существование записи для данного пользователя, недели и года
                    pay_sheet = PaySheetModel.objects.get(user=user, year=data['year'], week=data['week'])
                    # Обновляем поля записи данными из запроса
                    pay_sheet.role = data['role']
                    pay_sheet.role_salary = data['role_salary']
                    pay_sheet.hours = data['hours']
                    pay_sheet.salary = data['salary']
                    pay_sheet.works = data['works']
                    pay_sheet.count_of_12 = data['count_of_12']
                    pay_sheet.kf = data['kf']
                    pay_sheet.result_salary = data['result_salary']
                    pay_sheet.bonus = data['bonus']
                    pay_sheet.penalty = data['penalty']
                    pay_sheet.comment = data['comment']
                    pay_sheet.save()
                except PaySheetModel.DoesNotExist:
                    # Если запись не существует, создаем новую
                    pay_sheet = PaySheetModel(
                        user=user,
                        year=data['year'],
                        week=data['week'],
                        role=data['role'],
                        role_salary=data['role_salary'],
                        hours=data['hours'],
                        salary=data['salary'],
                        works=data['works'],
                        count_of_12=data['count_of_12'],
                        kf=data['kf'],
                        result_salary=data['result_salary'],
                        bonus=data['bonus'],
                        penalty=data['penalty'],
                        comment=data['comment'],
                    )
                    pay_sheet.save()

            return JsonResponse({'message': 'Успешно'})
        except Exception as ex:
            print(ex)
            return JsonResponse({'message': 'Произошла ошибка'})

    except Exception as ex:
        print(ex)
        return JsonResponse({'message': 'Произошла ошибка'})


def clean_data_post(row):
    output_row = [i.replace('\n', '')
                  .replace('  ', '')
                  .replace('Все работы', '')
                  .replace('р.', '')
                  .replace('%', '')
                  .replace('ч.', '')
                  .replace(',', '.')
                  .replace('руб/час', '').strip()
                  for i in row]
    return output_row
