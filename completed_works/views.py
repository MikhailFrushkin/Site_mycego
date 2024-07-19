import datetime
import re
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, FormView, TemplateView, DetailView
from loguru import logger

from users.models import CustomUser
from utils.utils import get_year_week
from work_schedule.models import Appointment
from .forms import WorkRecordForm, WorkRecordQuantityForm, WorkRecordFormAdmin, WorkRecordDeliveryForm, \
    WorkRecordFormDeliveryAdmin
from .models import WorkRecordQuantity, Standards, WorkRecord, Delivery, DeliveryWorks, DeliveryState, DeliveryNums


def remove_special_characters(input_string):
    # Создаем таблицу для перевода управляющих символов в None
    remove_chars = "\n\t\r"  # Добавьте другие символы по мере необходимости
    translator = str.maketrans('', '', remove_chars)

    # Применяем таблицу к строке
    cleaned_string = input_string.translate(translator)

    return cleaned_string


def create_work_record(request):
    # Проверка
    # # Получаем все работы, которые не архивированы
    # non_archived_standards = Standards.objects.filter(archive=False)
    #
    # # Получаем работы, которые не указаны ни в одном из отделов
    # standards_not_in_any_department = non_archived_standards.exclude(
    #     id__in=DepartmentWorks.objects.values_list('works__id', flat=True)
    # )
    #
    #
    # # Получаем работы, которые повторяются в нескольких отделах
    # repeated_standards = DepartmentWorks.objects.values('works').annotate(num_departments=Count('department')).filter(
    #     num_departments__gt=1)
    #
    # # Фильтруем неархивированные работы из повторяющихся и выводим информацию о отделах
    # for item in repeated_standards:
    #     standard_id = item['works']
    #     departments = DepartmentWorks.objects.filter(works=standard_id).values_list('department__name', flat=True)
    #     standard = Standards.objects.get(pk=standard_id)
    #     print(f"Работа '{standard.name}' повторяется в отделах: {', '.join(departments)}")
    #
    # print("\nРаботы, которые не указаны ни в одном из отделов:")
    # for standard in standards_not_in_any_department:
    #     print(standard.name)

    form = WorkRecordForm(user=request.user)
    if request.method == 'POST':
        form = WorkRecordForm(request.POST, user=request.user)
        if form.is_valid():
            pprint(request.POST)

            work_record = form.save(commit=False)
            work_record.user = request.user
            work_record.is_checked = False

            date = request.POST['date']
            date_today = datetime.datetime.now().date()
            date_last_chance = date_today - datetime.timedelta(days=7)
            year, month, day = map(int, date.split('-', maxsplit=3))
            date_result = datetime.date(year=year, month=month, day=day)
            if not date_last_chance <= date_result <= date_today:
                messages.error(request,
                               'Укажите верную дату работ, не раньше, '
                               'чем за неделю до сегодняшнего дня и не позже сегодняшнего дня!')
                return render(request, 'completed_works/completed_works.html', {'form': form})
            comment = request.POST['comment']
            cleaned_text = remove_special_characters(comment).strip()
            try:
                dep_name = request.user.department.name
            except Exception as ex:
                logger.error(f'{request.user} нет отдела')
                dep_name = ''
            work_record.comment = f"{dep_name}. {cleaned_text}"
            over_work_list = ['Другие работы(в минутах)', 'Грузчик', 'План', 'Обучение 3Д']
            over_work = []
            for work in over_work_list:
                get_comm = request.POST.get(work, None)
                if get_comm:
                    over_work.append(get_comm)
            errors = False

            if len(cleaned_text) == 0 and over_work:
                messages.error(request, 'Вы указали "Другие работы, Грузчик, План или Обучение 3Д" уточните '
                                        'пожалуйста в комментарии об этих работах')
                errors = True
            if len(cleaned_text) < 5:
                messages.error(request, 'Опишите более подробно')
                errors = True

            if errors:
                return render(request, 'completed_works/completed_works.html', {'form': form})

            existing_record = WorkRecord.objects.filter(user=work_record.user, date=date, delivery=None).first()
            if existing_record:
                messages.error(request, 'Запись уже существует для этой даты.')
                return redirect('completed_works:completed_works_view')

            standards = request.user.role.works_standards.all()
            # Проверка, что все поля quantity не равны нулю
            has_non_zero_quantity = False
            for standard in standards:
                quantity = form.cleaned_data.get(standard.name, None)
                if quantity is not None and quantity != 0:
                    has_non_zero_quantity = True
                    break

            if has_non_zero_quantity:
                work_record.save()
                for standard in standards:
                    quantity = form.cleaned_data.get(standard.name, None)
                    if quantity:
                        WorkRecordQuantity.objects.create(work_record=work_record, standard=standard,
                                                          quantity=quantity)
                return redirect('completed_works:completed_works_view')
            else:
                messages.error(request, 'Ни одно количество не указано или все равно нулю.')
                return render(request, 'completed_works/completed_works.html', {'form': form})

    return render(request, 'completed_works/completed_works.html', {'form': form})


def create_work_record_delivery(request):
    form = WorkRecordDeliveryForm(user=request.user)
    template_name = 'completed_works/completed_works_delivery.html'
    if request.method == 'POST':
        form = WorkRecordDeliveryForm(request.POST, user=request.user)
        if form.is_valid():
            work_record = form.save(commit=False)

            work_record.user = request.user
            work_record.is_checked = False
            delivery_id = request.POST.get('delivery', None)
            if delivery_id:
                logger.debug(delivery_id)
                try:
                    # Преобразование delivery_id в целое число
                    delivery_id = int(delivery_id)
                    work_record.delivery = Delivery.objects.get(id=delivery_id)
                except (ValueError, Delivery.DoesNotExist) as ex:
                    logger.error(ex)
                    messages.error(request, 'Выбрана неверная поставка.')
                    return render(request, template_name, {'form': form})

            standards = Standards.objects.filter(delivery=True)

            # Проверка, что все поля quantity не равны нулю
            has_non_zero_quantity = False
            for standard in standards:
                quantity = form.cleaned_data.get(standard.name, None)
                if quantity is not None and quantity != 0:
                    has_non_zero_quantity = True
                    break

            if has_non_zero_quantity:
                work_record.save()
                for standard in standards:
                    quantity = form.cleaned_data.get(standard.name, None)
                    if quantity:
                        WorkRecordQuantity.objects.create(work_record=work_record, standard=standard,
                                                          quantity=quantity)
                return redirect('completed_works:completed_works_view')
            else:
                messages.error(request, 'Ни одно количество не указано или все равно нулю.')
                return render(request, template_name, {'form': form})

    return render(request, template_name, {'form': form})


def create_work_record_admin_add(request):
    form = WorkRecordFormAdmin()

    if request.method == 'POST' and request.user.is_staff:
        users = CustomUser.objects.filter(status_work=True).order_by('username')
        try:
            print(request.POST)
            form = WorkRecordForm(request.POST)
            work_record = form.save(commit=False)
            work_record.is_checked = False

            if request.POST.get('date', None) and request.POST.get('user', None):
                user = CustomUser.objects.get(id=request.POST['user'])
                work_record.user = user
                work_record.date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d')
                delivery_id = request.POST.get('delivery', None)

                comment = request.POST['comment']
                cleaned_text = remove_special_characters(comment).strip()

                try:
                    exec_work_records = WorkRecord.objects.get(user=work_record.user, date=work_record.date,
                                                               delivery=None)
                    messages.error(request, 'Запись на эту дату существует')
                    return render(request, 'completed_works/completed_works_admin_add.html',
                                  {'form': form, 'users': users})
                except Exception as ex:
                    logger.error(ex)

                over_work = request.POST.get('Другие работы(в минутах)', None)
                if len(cleaned_text) == 0 and over_work:
                    logger.error(len(cleaned_text))
                    messages.error(request,
                                   'Вы указали "Другие работы" уточните пожалуйста в комментарии об этих работах')
                    return render(request, 'completed_works/completed_works_admin_add.html',
                                  {'form': form, 'users': users})

                if delivery_id:
                    logger.debug(delivery_id)
                    try:
                        # Преобразование delivery_id в целое число
                        delivery_id = int(delivery_id)
                        work_record.delivery = Delivery.objects.get(id=delivery_id)
                    except (ValueError, Delivery.DoesNotExist) as ex:
                        logger.error(ex)
                        messages.error(request, 'Выбрана неверная поставка.')
                        return render(request, 'completed_works/completed_works.html', {'form': form, 'users': users})

                standards = Standards.objects.all()

                # Проверка, что все поля quantity не равны нулю
                has_non_zero_quantity = False
                for standard in standards:
                    quantity = request.POST.get(standard.name, None)
                    if quantity is not None and quantity != 0 and quantity != '':
                        has_non_zero_quantity = True
                        break
                if has_non_zero_quantity:
                    work_record.save()
                    for standard in standards:
                        quantity = request.POST.get(standard.name, None)
                        if quantity:
                            WorkRecordQuantity.objects.create(work_record=work_record, standard=standard,
                                                              quantity=quantity)
                    messages.success(request, 'Успешно')
                    return redirect('completed_works:completed_works_view_admin_add')
                else:
                    messages.error(request, 'Ни одно количество не указано или все равно нулю.')
                    return render(request, 'completed_works/completed_works_admin_add.html',
                                  {'form': form, 'users': users})

            else:
                # Сохраняем ошибку в сообщениях
                messages.error(request, 'Ошибки в полях')

                return render(request, 'completed_works/completed_works_admin_add.html', {'form': form, 'users': users})

        except Exception as ex:
            logger.error(ex)

    return render(request, 'completed_works/completed_works_admin_add.html', {'form': form})


def create_work_record_admin_add_delivery(request):
    template_name = 'completed_works/completed_works_admin_add_delivery.html'
    form = WorkRecordFormDeliveryAdmin()
    if request.method == 'POST' and request.user.is_staff:
        try:
            work_record = form.save(commit=False)
            work_record.is_checked = False

            if request.POST['date'] != '' and request.POST['user'] != '' and request.POST['delivery'] != '':
                work_record.user = CustomUser.objects.get(id=request.POST['user'])
                work_record.date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d')
                delivery_id = request.POST.get('delivery', None)
                if delivery_id:
                    logger.debug(delivery_id)
                    try:
                        # Преобразование delivery_id в целое число
                        delivery_id = int(delivery_id)
                        work_record.delivery = Delivery.objects.get(id=delivery_id)
                    except (ValueError, Delivery.DoesNotExist) as ex:
                        logger.error(ex)
                        messages.error(request, 'Выбрана неверная поставка.')
                        return render(request, template_name, {'form': form})

                standards = Standards.objects.filter(delivery=True)

                # Проверка, что все поля quantity не равны нулю
                has_non_zero_quantity = False
                for standard in standards:
                    quantity = request.POST.get(standard.name, None)
                    if quantity is not None and quantity != 0 and quantity != '':
                        has_non_zero_quantity = True
                        break
                if has_non_zero_quantity:
                    work_record.save()
                    for standard in standards:
                        quantity = request.POST.get(standard.name, None)
                        if quantity:
                            WorkRecordQuantity.objects.create(work_record=work_record, standard=standard,
                                                              quantity=quantity)
                    messages.success(request, 'Успешно')
                    return redirect('completed_works:completed_works_delivery_admin')
                else:
                    messages.error(request, 'Ни одно количество не указано или все равно нулю.')
                    return render(request, template_name, {'form': form})

            else:
                # Сохраняем ошибку в сообщениях
                messages.error(request, 'Ошибки в полях')

                # Заполняем форму данными из POST-запроса
                form.fields['hours'].initial = request.POST['hours']
                form.fields['date'].initial = request.POST['date']
                form.fields['user'].initial = request.POST['user']
                return render(request, template_name, {'form': form})

        except Exception as ex:
            logger.error(ex)

    return render(request, template_name, {'form': form})


class ViewWorks(LoginRequiredMixin, ListView, FormView):
    model = CustomUser
    form_class = WorkRecordQuantityForm
    template_name = 'completed_works/view_works.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('completed_works:completed_works_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work_records_data = []

        user = CustomUser.objects.get(pk=self.request.user.pk)
        # Получите все записи работы пользователя и аннотируйте их суммарное количество работы
        work_lists = WorkRecord.objects.filter(user=user).order_by('-date')

        for work_list in work_lists:
            work_record_data = {
                'id': work_list.id,
                'user': work_list.user,
                'date': work_list.date,
                'hours': work_list.hours,
                'is_checked': work_list.is_checked,
                'delivery': work_list.delivery,
                'works': work_list.workrecordquantity_set.values('id', 'standard__name', 'quantity')
            }
            work_records_data.append(work_record_data)

        context['work_records_data'] = work_records_data  # Добавьте данные в контекст
        return context


def update_work_quantities(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                work_record_quantity_id = key.split('_')[1]
                work_record_quantity = WorkRecordQuantity.objects.get(pk=work_record_quantity_id)
                form = WorkRecordQuantityForm({'quantity': value}, instance=work_record_quantity)
                related_work_record = work_record_quantity.work_record
                if form.is_valid():
                    form.save()
        if request.user.is_staff:
            related_work_record.is_checked = True
            related_work_record.save()
            return redirect('completed_works:completed_works_view_admin')
    return redirect('completed_works:completed_works_view')


def delete_work_record(request, work_record_id):
    # Получите объект WorkRecord по его идентификатору
    work_record = WorkRecord.objects.get(id=work_record_id)
    logger.debug(work_record)
    # Проверьте, что текущий пользователь равен владельцу записи и is_checked=False
    if request.method == 'DELETE' and request.user.is_staff:
        work_record.delete()
        return JsonResponse({'message': 'Appointment update successfully.'}, status=200)
    else:
        if request.user == work_record.user and not work_record.is_checked:
            work_record.delete()
    return redirect('completed_works:completed_works_view')


class ViewWorksAdmin(LoginRequiredMixin, ListView, FormView):
    model = WorkRecord
    form_class = WorkRecordQuantityForm
    template_name = 'completed_works/view_works_admin.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('completed_works:completed_works_view_admin')

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        year = self.request.GET.get('year')
        week = self.request.GET.get('week')
        if not year or not week:
            import datetime
            today = datetime.date.today()
            year = today.year
            week = today.isocalendar()[1]

        queryset = WorkRecord.objects.filter(
            date__year=year,
            date__week=week,
            delivery=None
        )
        logger.debug(queryset)
        self._queryset = queryset  # Сохраняем результат в атрибуте _queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        work_lists_dict = {}
        unique_dates = queryset.values_list('date', flat=True).distinct().order_by('date')
        for date in unique_dates:
            work_records_data = []
            flag = True

            work_lists = queryset.filter(date=date)

            for work_list in work_lists:
                work_record_data = {
                    'id': work_list.id,
                    'user': work_list.user,
                    'date': work_list.date,
                    'hours': work_list.hours,
                    'is_checked': work_list.is_checked,
                    'comment': work_list.comment,
                    'works': work_list.workrecordquantity_set.values('id', 'standard__name', 'quantity')
                }
                if not work_list.is_checked:
                    flag = False
                work_records_data.append(work_record_data)

            work_records_data = sorted(work_records_data, key=lambda x: x['is_checked'])
            work_lists_dict[date] = (work_records_data, flag)
        context['work_lists_dict'] = work_lists_dict
        context['year'], context['week'] = get_year_week(self.request.GET, 'list_work')
        return context


class ViewWorksDeliveryAdmin(LoginRequiredMixin, ListView, FormView):
    model = WorkRecord
    form_class = WorkRecordQuantityForm
    template_name = 'completed_works/view_works_admin_delivery.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('completed_works:delivery_view_admin')

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        year = self.request.GET.get('year')
        week = self.request.GET.get('week')
        if not year or not week:
            import datetime
            today = datetime.date.today()
            year = today.year
            week = today.isocalendar()[1]

        queryset = WorkRecord.objects.filter(
            date__year=year,
            date__week=week
        ).exclude(delivery=None)
        logger.debug(queryset)
        self._queryset = queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        work_lists_dict = {}
        unique_dates = queryset.values_list('date', flat=True).distinct().order_by('date')
        for date in unique_dates:
            work_records_data = []
            flag = True

            work_lists = queryset.filter(date=date)

            for work_list in work_lists:
                work_record_data = {
                    'id': work_list.id,
                    'user': work_list.user,
                    'date': work_list.date,
                    'hours': work_list.hours,
                    'is_checked': work_list.is_checked,
                    'comment': work_list.comment,
                    'works': work_list.workrecordquantity_set.values('id', 'standard__name', 'quantity'),
                    'delivery': work_list.delivery
                }
                if not work_list.is_checked:
                    flag = False
                work_records_data.append(work_record_data)

            work_records_data = sorted(work_records_data, key=lambda x: x['is_checked'])
            work_lists_dict[date] = (work_records_data, flag)
        context['work_lists_dict'] = work_lists_dict
        context['year'], context['week'] = get_year_week(self.request.GET, 'list_work')
        return context


def save_all_row(request, week):
    if request.user.is_staff:
        works_records = WorkRecord.objects.filter(date__week=week, delivery=None)
        print(len(works_records))
        for item in works_records:
            item.is_checked = True
            item.save()
        messages.success(request, f'Все записи сохранены за {week} неделю')
        redirect('completed_works:completed_works_view_admin')
    return redirect('completed_works:completed_works_view_admin')


class WorkRecordDetailView(LoginRequiredMixin, DetailView):
    model = WorkRecord
    template_name = 'completed_works/view_works_details.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('completed_works:workrecord_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        works = WorkRecordQuantity.objects.filter(work_record=self.object, quantity__gt=0)
        context['works'] = works
        total_hours = \
            Appointment.objects.filter(user=self.object.user, date=self.object.date).aggregate(Sum('duration'))[
                'duration__sum']
        if total_hours:
            total_hours = total_hours.total_seconds() / 3600
        context['total_hours'] = total_hours
        return context


class AllDelivery(ListView):
    model = Delivery
    template_name = 'completed_works/delivery_all.html'
    context_object_name = 'delivery'

    def get_queryset(self):
        current_datetime = timezone.now()
        start_date = current_datetime - datetime.timedelta(days=5)
        queryset = (Delivery.objects.filter(
            Q(createdAt__gt=start_date))
                    .exclude(Q(products_nums_on_list={}) | Q(products_nums_on_list=None) | Q(products_nums_on_list=''))
                    .exclude(closedAt__isnull=False).order_by('createdAt'))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        delivery_badges = {}
        temp_q = queryset.filter(type_d='badges').order_by('state')
        for i in temp_q:
            state = DeliveryNums.objects.filter(delivery=i, status=False).order_by('state__number').first().state.name
            delivery_badges[i] = state
        context['delivery_badges'] = delivery_badges

        delivery_posters = {}
        temp_q = queryset.filter(type_d='posters').order_by('state')
        for i in temp_q:
            state = DeliveryNums.objects.filter(delivery=i, status=False).order_by('state__number').first().state.name
            delivery_posters[i] = state
        context['delivery_posters'] = delivery_posters

        return context


class DeliveryView(TemplateView):
    template_name = 'completed_works/delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delivery = Delivery.objects.get(id=context['delivery_id'])
        context['delivery'] = delivery

        delivery_works_by_state = {}
        if delivery.type_d == 'badges':
            type_state = 'Значки'
            states = DeliveryState.objects.filter(type=type_state).order_by('number')
        elif delivery.type_d == 'posters':
            type_state = 'Постеры'
            states = DeliveryState.objects.filter(type=type_state).order_by('number')
        else:
            messages.error(self.request, 'Ошибки в типе поставки')
            return HttpResponseRedirect(reverse_lazy('main_site:main_site'))
        for state in states:
            works = DeliveryWorks.objects.filter(delivery=delivery.id, state=state)
            delivery_nums = DeliveryNums.objects.get(delivery=delivery.id, state=state)
            delivery_works_by_state[state] = (works, delivery_nums)

        delivery.state = (DeliveryNums.objects.filter(delivery=delivery, status=False)
                          .order_by('state__number').first().state)
        delivery.save()

        context['delivery_works_by_state'] = delivery_works_by_state
        context['count_state'] = DeliveryState.objects.filter(type=type_state).count()
        return context


def cut_state(request, delivery_id, delivery_nums_id):
    if request.method == 'POST':
        user = request.user

        delivery = Delivery.objects.get(pk=delivery_id)
        arts_dict = delivery.products_nums_on_list
        nums = DeliveryNums.objects.get(id=delivery_nums_id)
        state = nums.state
        current_state = state.number
        after_state = current_state + 1
        # nums2 = DeliveryNums.objects.get(delivery=delivery.id, state__number=after_state)

        if state.num_emp == 1:
            nums_av = nums.available_numbers
            [nums.ready_numbers.append(i) for i in nums_av]
            nums.save()

            # [nums2.available_numbers.append(i) for i in nums_av]
            # nums2.save()

            work_record = WorkRecord.objects.create(user=user, date=datetime.date.today(), delivery=delivery)
            work_record.save()
            standard = state.standard
            quantity = 0
            if state.type_quantity == 'В листах':
                if delivery.type_d == 'posters':
                    quantity = sum(arts_dict[str(i)].get('quantity') for i in nums_av)
            elif state.type_quantity == 'В кол-во арт.':
                quantity = len(nums_av)
            elif state.type_quantity == 'В шт.':
                quantity = sum(arts_dict[str(i)].get('quantity') for i in nums_av)

            if current_state == 1:
                if delivery.machin == 'Большой принтер':
                    if delivery.type_d == 'badges':
                        standard = Standards.objects.get(name='Печать постеров КОНИКА( в листах)')
                    elif delivery.type_d == 'posters':
                        standard = Standards.objects.get(name='Печать постеров КОНИКА( в листах)')

                quantity = delivery.lists

            work = WorkRecordQuantity.objects.create(work_record=work_record,
                                                     standard=standard,
                                                     quantity=quantity)
            work.save()

            delivery_works = DeliveryWorks(
                delivery=delivery,
                state=state,
                user=user,
                nums=nums_av,
                quantity=quantity
            )
            delivery_works.save()
            messages.success(request, 'Успешно!')
        else:
            user = request.user
            numbers: str = request.POST.get('numbers', None)
            message = (f'Ошибка во вводе номеров!{numbers}'
                       '\nУказать номера необходимо через пробел,'
                       ' запятую или же через "-"(интервал с и по какой номер).')

            if not numbers:
                messages.error(request, f'Не указан номер(а)!')
                return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))
            if 'все' in numbers.lower() or 'всё' in numbers.lower():
                take_nums = nums.available_numbers
            else:
                numbers = re.sub(r'[^0-9\s, -]+', '', numbers)

                if '-' in numbers:
                    number_from, number_to = int(numbers.split('-')[0]), int(numbers.split('-')[1])
                    if (delivery.products_count >= number_from > 0
                            and delivery.products_count >= number_to > 0
                            and number_to >= number_from):
                        take_nums = list(range(number_from, number_to + 1))
                    else:
                        messages.error(request, message)
                        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))

                elif ',' in numbers:
                    take_nums = sorted(list(set(int(i.strip()) for i in numbers.split(',') if i)))
                    if not take_nums:
                        messages.error(request, message)
                        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))
                else:
                    take_nums = sorted(list(set(int(i.strip()) for i in numbers.split() if i)))
                    if not take_nums:
                        messages.error(request, message)
                        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))

            av_nums = set(nums.available_numbers)
            result = set(take_nums) - av_nums
            if len(result) == 0:
                [nums.ready_numbers.append(i) for i in take_nums]
                nums.save()
                # [nums2.available_numbers.append(i) for i in take_nums]
                # nums2.save()

                work_record = WorkRecord.objects.create(user=user, date=datetime.date.today(), delivery=delivery)
                work_record.save()

                standard = state.standard
                quantity = 0
                if state.type_quantity == 'В листах':
                    quantity = sum(arts_dict[str(i)].get('quantity') for i in take_nums)
                elif state.type_quantity == 'В кол-во арт.':
                    quantity = len(take_nums)
                elif state.type_quantity == 'В шт.':
                    quantity = sum(arts_dict[str(i)].get('quantity') for i in take_nums)
                work = WorkRecordQuantity.objects.create(work_record=work_record,
                                                         standard=standard,
                                                         quantity=quantity)
                work.save()

                delivery_works = DeliveryWorks(
                    delivery=delivery,
                    state=nums.state,
                    user=user,
                    nums=take_nums,
                    quantity=quantity
                )
                delivery_works.save()

                messages.success(request, 'Успешно!')
            else:
                result_str = ", ".join(map(str, result))
                messages.error(request, f'Эти номера не доступны: {result_str}')

        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))
