from django.contrib import admin

from pay_sheet.models import PaySheetModel, PaySheetMonthModel


class AdminPaySheetModel(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'year', 'week', 'role', 'role_salary', 'hours', 'salary',
        'works', 'count_of_12', 'kf', 'bonus', 'penalty', 'result_salary', 'comment',
        'created_at', 'updated_at'
              )
    list_filter = ['user', 'year', 'week', 'role']
    fields = (
        'user', 'year', 'week', 'role', 'role_salary', 'hours', 'salary',
        'works', 'count_of_12', 'kf', 'bonus', 'penalty', 'result_salary', 'comment',
              )


admin.site.register(PaySheetModel, AdminPaySheetModel)


class AdminPaySheetMonthModel(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'year', 'month', 'role', 'role_salary', 'hours', 'salary',
        'works', 'count_of_12', 'kf', 'bonus', 'penalty', 'result_salary', 'comment',
        'created_at', 'updated_at'
              )
    list_filter = ['user', 'year', 'month', 'role']
    fields = (
        'user', 'year', 'month', 'role', 'role_salary', 'hours', 'salary',
        'works', 'count_of_12', 'kf', 'bonus', 'penalty', 'result_salary', 'comment',
              )


admin.site.register(PaySheetMonthModel, AdminPaySheetMonthModel)


