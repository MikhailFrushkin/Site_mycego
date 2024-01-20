import datetime as dt

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from loguru import logger

from .models import Appointment, VacationRequest

HOUR_CHOICES = []
current_time = dt.time(9, 0)  # Начинаем с 9:00
end_time = dt.time(20, 0)  # Завершаем в 23:00

while current_time != dt.time(0, 0) and current_time <= end_time:
    HOUR_CHOICES.append((current_time.strftime('%H:%M'), current_time.strftime('%H:%M')))
    current_time = (dt.datetime.combine(dt.date(1, 1, 1), current_time) + dt.timedelta(minutes=60)).time()

HOUR_CHOICES2 = []
current_time = dt.time(10, 0)  # Начинаем с 10:00
end_time = dt.time(21, 0)  # Завершаем в 23:00

while current_time != dt.time(0, 0) and current_time <= end_time:
    HOUR_CHOICES2.append((current_time.strftime('%H:%M'), current_time.strftime('%H:%M')))
    current_time = (dt.datetime.combine(dt.date(1, 1, 1), current_time) + dt.timedelta(minutes=60)).time()


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'start_time', 'end_time', 'comment', 'user_id']

    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.ChoiceField(
        choices=HOUR_CHOICES,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    end_time = forms.ChoiceField(
        choices=HOUR_CHOICES2,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )


class VacationRequestForm(forms.ModelForm):
    class Meta:
        model = VacationRequest
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        errors = []
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = timezone.now().date()

        if start_date and end_date:
            delta = end_date - start_date
            if delta.days < 7:
                errors.append(ValidationError("Продолжительность отпуска должна быть не менее 7 дней."))

            if start_date < today:
                errors.append(ValidationError("Дата начала отпуска не может быть меньше текущей даты."))

        if errors:
            for error in errors:
                self.add_error(None, error)

        return cleaned_data
