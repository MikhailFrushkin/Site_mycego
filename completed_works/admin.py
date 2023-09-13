from django.contrib import admin
from .models import Standards, WorkRecord, WorkRecordQuantity

admin.site.register(Standards)
admin.site.register(WorkRecord)
admin.site.register(WorkRecordQuantity)
