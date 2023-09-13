from django.urls import path

from .views import create_work_record, ViewWorks, ViewWorksAdmin, update_work_quantities

app_name = 'completed_works'

urlpatterns = [
    path('completed_works/', create_work_record, name='completed_works'),
    path('completed_works_view/', ViewWorks.as_view(), name='completed_works_view'),
    path('completed_works_view_admin/', ViewWorksAdmin.as_view(), name='completed_works_view_admin'),
    path('update_work_quantities/', update_work_quantities, name='update_work_quantities'),
]