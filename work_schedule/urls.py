from django.urls import path

from .views import WorkSchedule, EditWork, ajax_view, delete_appointment

app_name = 'work'

urlpatterns = [
    path('', WorkSchedule.as_view(), name='work_page'),
    path('edit_work/', EditWork.as_view(), name='edit_work'),
    path('delete_row/', delete_appointment, name='delete_row'),
    path('ajax/', ajax_view, name='ajax_view'),
]
