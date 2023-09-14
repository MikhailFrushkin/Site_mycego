import datetime
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from users.models import CustomUser
from .forms import WorkRecordForm, WorkRecordQuantityForm
from .models import WorkRecordQuantity, Standards, WorkRecord


def create_work_record(request):
    if request.method == 'POST':
        form = WorkRecordForm(request.POST)
        if form.is_valid():
            work_record = form.save(commit=False)

            work_record.user = request.user
            work_record.date = datetime.datetime.today()
            work_record.is_checked = False

            # Проверка, что все поля quantity не равны нулю
            has_non_zero_quantity = False
            for standard in Standards.objects.all():
                quantity = form.cleaned_data.get(standard.name, None)
                if quantity is not None and quantity != 0:
                    has_non_zero_quantity = True
                    break

            if has_non_zero_quantity:
                work_record.save()
                for standard in Standards.objects.all():
                    quantity = form.cleaned_data.get(standard.name, None)
                    print(standard, quantity)
                    if not quantity:
                        quantity = 0
                    WorkRecordQuantity.objects.create(work_record=work_record, standard=standard, quantity=quantity)
                return redirect('completed_works:completed_works_view')
            else:
                # Если нет непустых количеств, не сохраняем запись
                print('Ни одно количество не указано или все равно нулю.')
                messages.error(request, 'Ни одно количество не указано или все равно нулю.')
                return render(request, 'completed_works/completed_works.html', {'form': form})
    else:
        user = request.user
        date = datetime.datetime.today()

        existing_record = WorkRecord.objects.filter(user=user, date=date).first()
        if existing_record:
            messages.error(request, 'Запись уже существует для этой даты.')
            return redirect('completed_works:completed_works_view')
        form = WorkRecordForm()

    return render(request, 'completed_works/completed_works.html', {'form': form})


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
        work_lists = WorkRecord.objects.filter(user=user).order_by('date')

        for work_list in work_lists:
            work_record_data = {
                'user': work_list.user,
                'date': work_list.date,
                'is_checked': work_list.is_checked,
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


class ViewWorksAdmin(LoginRequiredMixin, ListView, FormView):
    model = CustomUser
    form_class = WorkRecordQuantityForm
    template_name = 'completed_works/view_works_admin.html'
    login_url = '/users/login/'
    success_url = reverse_lazy('completed_works:completed_works_view_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work_lists_dict = {}
        unique_dates = WorkRecord.objects.values_list('date', flat=True).distinct().order_by('date')
        for date in unique_dates:
            work_records_data = []
            flag = True

            work_lists = WorkRecord.objects.filter(date=date)

            for work_list in work_lists:
                work_record_data = {
                    'user': work_list.user,
                    'date': work_list.date,
                    'is_checked': work_list.is_checked,
                    'works': work_list.workrecordquantity_set.values('id', 'standard__name', 'quantity')
                }
                if not work_list.is_checked:
                    flag = False
                work_records_data.append(work_record_data)

            work_records_data = sorted(work_records_data, key=lambda x: x['is_checked'])
            work_lists_dict[date] = (work_records_data, flag)
        context['work_lists_dict'] = work_lists_dict
        return context
