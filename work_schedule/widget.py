from django import forms


class TimePickerInput(forms.TimeInput):
    input_type = 'time'

    def __init__(self, attrs=None, format=None, step=None, initial=None):
        super().__init__(attrs=attrs, format=format)
        self.attrs['step'] = step
        self.initial = initial