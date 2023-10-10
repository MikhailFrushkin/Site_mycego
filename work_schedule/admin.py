from django.contrib import admin

from work_schedule.models import Appointment, VacationRequest, FingerPrint, BadFingerPrint


class WorkSchedule(admin.ModelAdmin):
    list_display = [field.name for field in Appointment._meta.fields]
    list_editable = ['date', 'start_time', 'end_time', 'verified']
    list_filter = ['date', 'verified']
    search_fields = ('user__username',)
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


class AdminFingerPrint(admin.ModelAdmin):
    list_display = [field.name for field in FingerPrint._meta.fields]
    search_fields = ('user__username',)


admin.site.register(FingerPrint, AdminFingerPrint)


class AdminBadFingerPrint(admin.ModelAdmin):
    list_display = [field.name for field in BadFingerPrint._meta.fields]
    search_fields = ('user__username',)


admin.site.register(BadFingerPrint, AdminBadFingerPrint)
