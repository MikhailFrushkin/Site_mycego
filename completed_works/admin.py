from django.contrib import admin
from .models import Standards, WorkRecord, WorkRecordQuantity


class AdminStandards(admin.ModelAdmin):
    list_display = [field.name for field in Standards._meta.fields]
    list_editable = ['name', 'standard', 'type_for_printer']
    list_filter = ['name', 'standard', 'type_for_printer']
    list_per_page = 30


admin.site.register(Standards, AdminStandards)


class AdminWorkRecord(admin.ModelAdmin):
    list_display = [field.name for field in WorkRecord._meta.fields]
    list_editable = ['is_checked']
    list_filter = ['is_checked', 'works', 'user', 'date']
    list_per_page = 30


admin.site.register(WorkRecord, AdminWorkRecord)


class AdminWorkRecordQuantity(admin.ModelAdmin):
    list_display = [field.name for field in WorkRecordQuantity._meta.fields]
    list_editable = ['quantity']
    list_filter = ['work_record', 'standard']
    list_per_page = 30


admin.site.register(WorkRecordQuantity, AdminWorkRecordQuantity)
