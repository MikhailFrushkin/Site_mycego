from django import forms
from .models import WorkRecord, Standards, WorkRecordQuantity


class WorkRecordForm(forms.ModelForm):
    class Meta:
        model = WorkRecord
        fields = ['works']  # Выбираем поля, которые будут отображаться в форме

    # Добавляем поля для количества работы напротив каждого вида работ
    def __init__(self, *args, **kwargs):
        super(WorkRecordForm, self).__init__(*args, **kwargs)
        del self.fields['works']

        for standard in Standards.objects.all():
            self.fields[f'{standard.name}'] = forms.IntegerField(
                label=standard.name,
                initial=0,
                required=False
            )


class WorkRecordQuantityForm(forms.ModelForm):
    class Meta:
        model = WorkRecordQuantity
        fields = ['quantity']