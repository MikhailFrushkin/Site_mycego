from django.contrib import admin
from work_schedule.models import Appointment


class WorkSchedule(admin.ModelAdmin):
    list_display = [field.name for field in Appointment._meta.fields]
    list_editable = ['date', 'start_time', 'end_time', 'verified']
    list_filter = ['date', 'verified']
    list_per_page = 30
    fields = ('user', 'date', 'start_time', 'end_time', 'comment', 'duration', 'verified')


admin.site.register(Appointment, WorkSchedule)




