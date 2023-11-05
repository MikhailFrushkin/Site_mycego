from django.contrib import admin
from .models import Standards, WorkRecord, WorkRecordQuantity, Delivery, DeliveryState, DeliveryWorks, DeliveryNums


class AdminDeliveryNums(admin.ModelAdmin):
    list_display = [field.name for field in DeliveryNums._meta.fields]
    list_filter = ('status',)
    search_fields = ('delivery__name',)
    list_per_page = 100


admin.site.register(DeliveryNums, AdminDeliveryNums)


class AdminDeliveryStage(admin.ModelAdmin):
    list_display = [field.name for field in DeliveryState._meta.fields]


admin.site.register(DeliveryState, AdminDeliveryStage)


class AdminDeliveryWorks(admin.ModelAdmin):
    list_display = [field.name for field in DeliveryWorks._meta.fields]


admin.site.register(DeliveryWorks, AdminDeliveryWorks)


class AdminStandards(admin.ModelAdmin):
    list_display = [field.name for field in Standards._meta.fields]
    list_editable = ['name', 'standard', 'type_for_printer']
    list_filter = ['name', 'standard', 'type_for_printer']
    list_per_page = 100


admin.site.register(Standards, AdminStandards)


class AdminWorkRecord(admin.ModelAdmin):
    list_display = [field.name for field in WorkRecord._meta.fields]
    list_editable = ['is_checked']
    list_filter = ['is_checked', 'works', 'user', 'date']
    list_per_page = 100


admin.site.register(WorkRecord, AdminWorkRecord)


class AdminWorkRecordQuantity(admin.ModelAdmin):
    list_display = [field.name for field in WorkRecordQuantity._meta.fields]
    list_editable = ['quantity']
    list_filter = ['work_record', 'standard', 'quantity']
    search_fields = ('work_record',)
    list_per_page = 100


admin.site.register(WorkRecordQuantity, AdminWorkRecordQuantity)


class AdminDelivery(admin.ModelAdmin):
    list_display = [
        'id',
        'id_wb',
        'name',
        'createdAt',
        'closedAt',
        'products_count',
        'price',
        'type',
        'updated_at'
    ]
    search_fields = ('id_wb', 'name')
    list_per_page = 100


admin.site.register(Delivery, AdminDelivery)
