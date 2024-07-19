from django.contrib import admin
from .models import Standards, WorkRecord, WorkRecordQuantity, Delivery, DeliveryState, DeliveryWorks, DeliveryNums


class AdminDelivery(admin.ModelAdmin):
    list_display = [
        'id',
        'id_wb',
        'name',
        'createdAt',
        'closedAt',
        'products_count',
        'state',
        'machin'
    ]
    search_fields = ('id_wb', 'name')
    list_per_page = 100


admin.site.register(Delivery, AdminDelivery)


class AdminDeliveryStage(admin.ModelAdmin):
    list_display = [field.name for field in DeliveryState._meta.fields]
    ordering = ('type', 'number')
    list_editable = ('type_quantity', )


admin.site.register(DeliveryState, AdminDeliveryStage)


class AdminStandards(admin.ModelAdmin):
    list_display = [field.name for field in Standards._meta.fields]
    list_editable = ['name', 'standard', 'type_for_printer', 'archive']
    list_filter = ['name', 'standard', 'type_for_printer', 'archive']
    ordering = ('archive',)
    list_per_page = 100


admin.site.register(Standards, AdminStandards)


class AdminWorkRecord(admin.ModelAdmin):
    list_display = [field.name for field in WorkRecord._meta.fields]
    list_editable = ['is_checked']
    list_filter = ['is_checked', 'works', 'user', 'date']
    list_per_page = 100


admin.site.register(WorkRecord, AdminWorkRecord)


