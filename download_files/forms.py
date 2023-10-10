from django import forms


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Файл Excel c никами  от Пальчиков', required=False)
    excel_file2 = forms.FileField(label='Файл TXT со сканера', required=False)

