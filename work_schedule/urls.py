from django.urls import path

from .views import WorkSchedule, ajax_view

app_name = 'work'

urlpatterns = [
    path('', WorkSchedule.as_view(), name='work_page'),
    path('ajax/', ajax_view, name='ajax_view'),
]
