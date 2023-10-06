from django.contrib import admin
from work_schedule.models import Appointment, VacationRequest


class WorkSchedule(admin.ModelAdmin):
    list_display = [field.name for field in Appointment._meta.fields]
    list_editable = ['date', 'start_time', 'end_time', 'verified']
    list_filter = ['date', 'verified']
    list_per_page = 30
    fields = ('user', 'date', 'start_time', 'end_time', 'comment', 'duration', 'verified')


admin.site.register(Appointment, WorkSchedule)


class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'duration')
    search_fields = ('employee__username',)  # Поиск по имени сотрудника

    def get_readonly_fields(self, request, obj=None):
        # Делаем поле "Продолжительность" только для чтения
        if obj:
            return ['duration']
        return []


admin.site.register(VacationRequest, VacationRequestAdmin)
