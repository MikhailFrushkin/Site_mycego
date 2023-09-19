from django import forms
from .models import WorkRecord, Standards, WorkRecordQuantity
from django.db.models import Q


class WorkRecordForm(forms.ModelForm):
    class Meta:
        model = WorkRecord
        fields = ['hours', 'works']  # Выбираем поля, которые будут отображаться в форме

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super(WorkRecordForm, self).__init__(*args, **kwargs)
        del self.fields['works']

        standards = Standards.objects.all()

        if user and user.role:
            try:
                if user.role.name == 'Печатник':
                    # Добавляем фильтрацию для роли 'Печатник', например, по имени стандарта
                    standards = standards.filter(Q(type_for_printer=True) | Q(name='Другие работы(в минутах)'))
                else:
                    standards = standards.filter(type_for_printer=False)
            except Exception as ex:
                print(ex)
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
