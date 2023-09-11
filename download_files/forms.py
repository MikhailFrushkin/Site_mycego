from django import forms


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Загрузите файл Excel (xlsx)')
