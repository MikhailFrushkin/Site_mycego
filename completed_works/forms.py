from django import forms
from datetime import datetime, timedelta
from django.utils import timezone
from users.models import CustomUser
from .models import WorkRecord, Standards, WorkRecordQuantity, Delivery
from django.db.models import Q


class WorkRecordDeliveryForm(forms.ModelForm):
    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=5)
    delivery = forms.ModelChoiceField(
        queryset=Delivery.objects.filter(
            Q(createdAt__gt=start_date) & ~Q(name__icontains='заказ') & ~Q(name__icontains='ЗАКАЗ') & ~Q(
                name__icontains='Заказ')
        ).order_by('-createdAt'),
        label='Поставка',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'}),
    )

    class Meta:
        model = WorkRecord
        fields = ['date', 'delivery']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs

        super(WorkRecordDeliveryForm, self).__init__(*args, **kwargs)
        standards = Standards.objects.all()

        for standard in standards.order_by('id'):
            if standard.delivery:
                self.fields[f'{standard.name}'] = forms.IntegerField(
                    label=standard.name,
                    initial=0,
                    required=False
                )


class WorkRecordFormDeliveryAdmin(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(status_work=True).order_by('username'),
        label='Сотрудник',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'})
    )
    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=5)
    delivery = forms.ModelChoiceField(
        queryset=Delivery.objects.filter(
            Q(createdAt__gt=start_date) & ~Q(name__icontains='заказ') & ~Q(name__icontains='ЗАКАЗ') & ~Q(
                name__icontains='Заказ')
        ).order_by('-createdAt'),
        label='Поставка',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'}),
    )

    class Meta:
        model = WorkRecord
        fields = ['user', 'date', 'delivery']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(WorkRecordFormDeliveryAdmin, self).__init__(*args, **kwargs)

        standards = Standards.objects.all()

        for standard in standards.order_by('id'):
            if standard.delivery:
                self.fields[f'{standard.name}'] = forms.IntegerField(
                    label=standard.name,
                    initial=0,
                    required=False
                )


class WorkRecordForm(forms.ModelForm):
    class Meta:
        model = WorkRecord
        fields = ['date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'comment': forms.Textarea(),
        }

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
    #     super(WorkRecordForm, self).__init__(*args, **kwargs)
    #     standards = Standards.objects.all()
    #
    #     if user and user.role:
    #         try:
    #             if user.role.name == 'Печатник':
    #                 # Добавляем фильтрацию для роли 'Печатник', например, по имени стандарта
    #                 standards = standards.filter(Q(type_for_printer=True) | Q(name='Другие работы(в минутах)'))
    #             else:
    #                 standards = standards.filter(type_for_printer=False)
    #         except Exception as ex:
    #             print(ex)
    #     for standard in standards.order_by('id'):
    #         self.fields[f'{standard.name}'] = forms.IntegerField(
    #             label=standard.name,
    #             initial=0,
    #             required=False
    #         )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super(WorkRecordForm, self).__init__(*args, **kwargs)
        standards = None
        if user and user.role:
            try:
                standards = user.role.works_standards.all()
            except Exception as ex:
                print(ex)
        if standards:
            for standard in standards.order_by('id'):
                self.fields[f'{standard.name}'] = forms.IntegerField(
                    label=standard.name,
                    initial=0,
                    required=False
                )

class WorkRecordFormAdmin(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(status_work=True).order_by('username'),
        label='Сотрудник',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'})
    )
    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=5)

    class Meta:
        model = WorkRecord
        fields = ['user', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(WorkRecordFormAdmin, self).__init__(*args, **kwargs)

        standards = Standards.objects.all()

        for standard in standards.order_by('id'):
            self.fields[f'{standard.name}'] = forms.IntegerField(
                label=standard.name,
                initial=0,
                required=False
            )


class WorkRecordQuantityForm(forms.ModelForm):
    class Meta:
        model = WorkRecordQuantity
        fields = ['quantity']
