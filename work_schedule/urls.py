from django.urls import path

from .views import WorkSchedule, EditWork, ajax_view, delete_appointment, update_appointment, GrafUser

app_name = 'work'

urlpatterns = [
    path('', WorkSchedule.as_view(), name='work_page'),
    path('edit_work/', EditWork.as_view(), name='edit_work'),
    path('graf_user/', GrafUser.as_view(), name='graf_user'),


    path('delete_row/', delete_appointment, name='delete_row'),
    path('update_rows/', update_appointment, name='update_rows'),
    path('ajax/', ajax_view, name='ajax_view'),
]
