from django.contrib import admin
from work_schedule.models import Appointment, Role, UserProfile


class WorkSchedule(admin.ModelAdmin):
    list_display = [field.name for field in Appointment._meta.fields]
    list_editable = ['date', 'start_time', 'end_time', 'verified']
    list_filter = ['date', 'verified']
    list_per_page = 30
    fields = ('user', 'date', 'start_time', 'end_time', 'comment', 'duration', 'verified')

admin.site.register(Appointment, WorkSchedule)
admin.site.register(Role)
admin.site.register(UserProfile)



