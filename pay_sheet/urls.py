from django.urls import path, reverse_lazy

from pay_sheet.views import PaySheet, created_salary_check, PaySheetListView, PaySheetDetailView, PaySheetMonth

app_name = 'pay_sheet'

urlpatterns = [
    path('', PaySheet.as_view(), name='pay_sheet'),
    path('month/', PaySheetMonth.as_view(), name='pay_sheet_month'),
    path('created_salary_check/', created_salary_check, name='created_salary_check'),
    path('list_user_pay_sheets/', PaySheetListView.as_view(), name='list_user_pay_sheets'),
    path('pay_sheet/<int:pk>/<str:model>/', PaySheetDetailView.as_view(), name='pay_sheet_detail'),
]
