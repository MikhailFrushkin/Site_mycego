import datetime
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
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
    form = WorkRecordForm(user=request.user)
    if request.method == 'POST':
        form = WorkRecordForm(request.POST, user=request.user)
        if form.is_valid():
            work_record = form.save(commit=False)
            pprint(request.POST)
            work_record.user = request.user
            work_record.is_checked = False

            date = request.POST['date']
            date_today = datetime.datetime.now().date()
            date_last_chance = date_today - datetime.timedelta(days=7)
            year, month, day = map(int, date.split('-', maxsplit=3))
            print(year, month, day)
            date_result = datetime.date(year=year, month=month, day=day)
            print(date_last_chance)
            print(date_result)
            if not date_last_chance <= date_result <= date_today:
                messages.error(request,
                               'Укажите верную дату работ, не раньше, '
                               'чем за неделю до сегодняшнего дня и не позже сегодняшнего дня!')
                return render(request, 'completed_works/completed_works.html', {'form': form})
            comment = request.POST['comment']
            cleaned_text = remove_special_characters(comment).strip()

            over_work = request.POST.get('Другие работы(в минутах)', None)
            if len(cleaned_text) == 0 and over_work:
                logger.error(len(cleaned_text))
                messages.error(request, 'Вы указали "Другие работы" уточните пожалуйста в комментарии об этих работах')
                return render(request, 'completed_works/completed_works.html', {'form': form})

            existing_record = WorkRecord.objects.filter(user=work_record.user, date=date, delivery=None).first()
            if existing_record:
                messages.error(request, 'Запись уже существует для этой даты.')
                return redirect('completed_works:completed_works_view')

            if work_record.user.role.name == 'Печатник':
                standards = Standards.objects.filter(Q(type_for_printer=True) | Q(name='Другие работы(в минутах)'))
            else:
                standards = Standards.objects.filter(type_for_printer=False)

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

                try:
                    exec_work_records = WorkRecord.objects.get(user=work_record.user, date=work_record.date)
                    messages.error(request, 'Запись на эту дату существует')
                    return render(request, 'completed_works/completed_works_admin_add.html',
                                  {'form': form, 'users': users})
                except Exception as ex:
                    logger.error(ex)

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
            date__week=week
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

            work_lists = queryset.filter(date=date, delivery=None)

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
        queryset = Delivery.objects.filter(
            Q(createdAt__gt=start_date) & ~Q(name__icontains='заказ') & ~Q(name__icontains='ЗАКАЗ') & ~Q(
                name__icontains='Заказ')
        ).exclude(closedAt__isnull=False).order_by('createdAt')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['delivery_badges'] = queryset.filter(type_d='badges')
        context['delivery_posters'] = queryset.filter(type_d='posters')
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

        context['delivery_works_by_state'] = delivery_works_by_state
        context['count_state'] = DeliveryState.objects.filter(type=type_state).count()
        return context


class DeliveryViewAdmin(ListView):
    model = Delivery
    template_name = 'completed_works/delivery_admin.html'


def cut_state(request, delivery_id, delivery_state_id):
    if request.method == 'POST':
        print(request.POST)
        delivery = Delivery.objects.get(pk=delivery_id)
        if delivery.type_d == 'badges':
            type_state = 'Значки'
        else:
            type_state = 'Постеры'
        state_after = DeliveryState.objects.get(type=type_state, number=delivery.state.number + 1)
        state_current = DeliveryState.objects.get(id=delivery_state_id)
        nums = DeliveryNums.objects.get(delivery=delivery.id, state=state_current)
        nums2 = DeliveryNums.objects.get(delivery=delivery.id, state=state_after)

        if state_current.num_emp == 1:
            [nums.ready_numbers.append(i) for i in nums.available_numbers]
            nums.save()

            [nums2.available_numbers.append(i) for i in nums.available_numbers]
            nums2.save()
            user = request.user
            delivery_works = DeliveryWorks(
                delivery=delivery,
                state=DeliveryState.objects.get(id=delivery_state_id),
                user=user,
                num_start=min(nums.available_numbers),
                num_end=max(nums.available_numbers),
            )
            delivery_works.save()
            delivery.state = state_after
            delivery.save()



            messages.success(request, 'Успешно!')
        else:
            user = request.user
            number_from = request.POST.get('number_range_form.number_from', None)
            number_to = request.POST.get('number_range_form.number_to', None)
            if number_from and number_to:
                number_from, number_to = int(number_from), int(number_to)
            if (delivery.products_count >= number_from > 0
                    and delivery.products_count >= number_to > 0
                    and number_to >= number_from):
                take_nums = set(range(number_from, number_to + 1))
                av_nums = set(nums.available_numbers)

                logger.debug(number_from)
                logger.debug(number_to)
                logger.debug(take_nums)
                logger.debug(av_nums)
                if len(take_nums - av_nums) == 0:
                    [nums.ready_numbers.append(i) for i in take_nums]
                    nums.save()
                    [nums2.available_numbers.append(i) for i in take_nums]
                    nums2.save()

                    delivery_works = DeliveryWorks(
                        delivery=delivery,
                        state=DeliveryState.objects.get(id=delivery_state_id),
                        user=user,
                        num_start=number_from,
                        num_end=number_to,
                    )
                    delivery_works.save()
                    delivery.state = state_after
                    delivery.save()

                    messages.success(request, 'Успешно!')
                else:
                    messages.error(request, 'Ошибка во вводе!')
            else:
                messages.error(request, 'Ошибка во вводе!')
        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))


def cut_state2(request, delivery_id, delivery_state_id):
    if request.method == 'POST':
        print(request.POST)
        delivery = Delivery.objects.get(pk=delivery_id)
        if delivery.type_d == 'badges':
            type_state = 'Значки'
        else:
            type_state = 'Постеры'
        state_after = DeliveryState.objects.get(type=type_state, number=delivery.state.number + 1)

        if delivery.state.num_emp == 1:
            user = request.user
            delivery_works = DeliveryWorks(
                delivery=delivery,
                state=DeliveryState.objects.get(id=delivery_state_id),
                user=user,
                num_start=1,
                num_end=delivery.products_count,
            )
            delivery_works.save()
            delivery.state = state_after
            delivery.save()
            messages.success(request, 'Успешно!')
            return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))
        else:
            user = request.user
            number_from = request.POST.get('number_range_form.number_from', None)
            number_to = request.POST.get('number_range_form.number_to', None)
            if number_from and number_to:
                number_from, number_to = int(number_from), int(number_to)
            if (number_from and number_to and delivery.products_count >= number_from > 0
                    and delivery.products_count >= number_to > 0 and number_to >= number_from):
                number_list = range(number_from, number_to + 1)

                get_list = []
                delivery_works = DeliveryWorks.objects.filter(
                    delivery=delivery,
                    state=DeliveryState.objects.get(id=delivery_state_id)
                )
                for item in delivery_works:
                    get_list.extend(range(item.num_start, item.num_end + 1))

                intersection = sorted(list(set(number_list) & set(get_list)))

                logger.debug(number_list)
                logger.debug(get_list)
                logger.debug(intersection)

                if not intersection:
                    if number_to > delivery.products_count:
                        messages.error(request, f'Указаные номера больше чем в поставке есть!')
                    else:
                        delivery_works = DeliveryWorks(
                            delivery=delivery,
                            state=DeliveryState.objects.get(id=delivery_state_id),
                            user=user,
                            num_start=number_from,
                            num_end=number_to,
                        )
                        delivery_works.save()
                        messages.success(request, 'Успешно!')

                        get_list = []
                        delivery_works = DeliveryWorks.objects.filter(
                            delivery=delivery,
                            state=DeliveryState.objects.get(id=delivery_state_id)
                        )
                        for item in delivery_works:
                            get_list.extend(range(item.num_start, item.num_end + 1))
                        if not set(range(1, delivery.products_count + 1)) - set(get_list):
                            delivery.state = state_after
                            delivery.save()

                        return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))
                else:
                    messages.error(request, f'Указаные номера уже сделаны: {", ".join(map(str, intersection))}')

            else:
                messages.error(request, 'Ошибки в указанных номерах, возможно указано больше чем есть в поставке')
            return HttpResponseRedirect(reverse_lazy('completed_works:delivery_view', args=[delivery_id]))

