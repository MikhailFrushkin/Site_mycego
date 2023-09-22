from django.urls import path, reverse_lazy

from pay_sheet.views import PaySheet, created_salary_check

app_name = 'pay_sheet'

urlpatterns = [
    path('', PaySheet.as_view(), name='pay_sheet'),
    path('created_salary_check/', created_salary_check, name='created_salary_check'),

]
