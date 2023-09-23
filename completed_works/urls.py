from django.urls import path

from .views import create_work_record, ViewWorks, ViewWorksAdmin, update_work_quantities, delete_work_record, create_work_record_admin_add, save_all_row

app_name = 'completed_works'

urlpatterns = [
    path('completed_works/', create_work_record, name='completed_works'),
    path('completed_works_view/', ViewWorks.as_view(), name='completed_works_view'),
    path('completed_works_view_admin/', ViewWorksAdmin.as_view(), name='completed_works_view_admin'),
    path('completed_works_view_admin_add/', create_work_record_admin_add, name='completed_works_view_admin_add'),
    path('delete_work_record/<int:work_record_id>/', delete_work_record, name='delete_work_record'),
    path('update_work_quantities/', update_work_quantities, name='update_work_quantities'),
    path('save_all/<int:week>/', save_all_row, name='save_all_row'),
]