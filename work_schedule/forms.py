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
    current_time = (dt.datetime.combine(dt.date(1, 1, 1), current_time) + dt.timedelta(minutes=60)).time()

HOUR_CHOICES2 = []
current_time = dt.time(10, 0)  # Начинаем с 9:00
end_time = dt.time(21, 0)  # Завершаем в 21:00

while current_time <= end_time:
    HOUR_CHOICES2.append((current_time, current_time.strftime('%H:%M')))
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

            # Определяем текущую неделю в году
            current_week = current_date.isocalendar()[1]

            # Добавляем 2 недели к текущей неделе
            target_week = current_week + 2

            # Определяем дату начала target_week (понедельник этой недели)
            start_date = current_date + dt.timedelta(weeks=target_week - current_week, days=-current_date.weekday())

            # Создаем список дней для target_week
            days_in_target_week = [start_date + dt.timedelta(days=i) for i in range(14)]
            end_day = start_date + dt.timedelta(days=14)
            # Проверяем, если дата входит в список дней target_week
            if date not in days_in_target_week:
                errors.append(ValidationError(f"Вы можете записаться на даты, начиная с {start_date} до  {end_day}."))



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
