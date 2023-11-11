from django.urls import path
from django.views.decorators.cache import cache_page
from .views import WorkSchedule, EditWork, ajax_view, delete_appointment, update_appointment, GrafUser, \
    VacationRequestCreateView, VacationRequestAdmin, delete_vacation, confirm_vacation, search_emp, FingerPrintView, \
    EditWorkMonth

app_name = 'work'

urlpatterns = [
    path('', WorkSchedule.as_view(), name='work_page'),
    path('edit_work/', EditWork.as_view(), name='edit_work'),
    path('edit_work_month/', EditWorkMonth.as_view(), name='edit_work_month'),
    path('graf_user/', GrafUser.as_view(), name='graf_user'),
    path('create_vacation_request/', VacationRequestCreateView.as_view(), name='create_vacation_request'),
    path('vacation_admin/', VacationRequestAdmin.as_view(), name='vacation_admin'),
    path('vacation_admin/delete_vacation/<int:vacation_id>/', delete_vacation, name='delete_vacation'),
    path('vacation_admin/confirm_vacation/<int:vacation_id>/', confirm_vacation, name='confirm_vacation'),
    path('finger_print/', FingerPrintView.as_view(), name='finger_print'),

    path('delete_row/', delete_appointment, name='delete_row'),
    path('update_rows/', update_appointment, name='update_rows'),
    path('ajax/', ajax_view, name='ajax_view'),
    path('ajax/search_emp/', search_emp, name='search_emp'),
]
