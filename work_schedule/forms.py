import datetime as dt

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Appointment

# Создайте список с интервалом в 30 минут от 9:00 до 21:00
HOUR_CHOICES = []
current_time = dt.time(9, 0)  # Начинаем с 9:00
end_time = dt.time(21, 0)  # Завершаем в 21:00

while current_time <= end_time:
    HOUR_CHOICES.append((current_time, current_time.strftime('%H:%M')))
    current_time = (dt.datetime.combine(dt.date(1, 1, 1), current_time) + dt.timedelta(minutes=30)).time()


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'start_time', 'end_time', 'comment', 'user_id']

    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.ChoiceField(
        choices=HOUR_CHOICES,
        initial='09:00',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    end_time = forms.ChoiceField(
        choices=HOUR_CHOICES,
        initial='21:00',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        user_id = cleaned_data.get('user_id')

        # Создаем список ошибок
        errors = []
        print('Проверяемая дата: ', cleaned_data)
        if date is None:
            errors.append(ValidationError("Не выбрана дата."))
        else:
            # Получаем текущую дату
            current_date = date.today()

            # Проверяем, что дата не младше 3 дней от текущей даты
            min_date = current_date + dt.timedelta(days=3)
            if date < min_date:
                errors.append(ValidationError("Дата должна быть не младше 3х дней от текущей даты."))

            # Проверяем, что дата не старше 1 месяца
            user_date = 30
            max_date = current_date + dt.timedelta(days=user_date)
            if date > max_date:
                errors.append(ValidationError(f"Дата не должна быть старше {user_date} месяца."))

        if start_time >= end_time:
            errors.append(ValidationError("Время начала должно быть меньше времени окончания."))

        existing_appointment = Appointment.objects.filter(
            Q(user_id=user_id),
            Q(date=date)
        )
        if existing_appointment.exists():
            errors.append(ValidationError("У вас уже есть запись на эту дату."))

        if errors:
            # Если есть ошибки, добавляем их в атрибуты формы
            for error in errors:
                self.add_error(None, error)

        return cleaned_data
