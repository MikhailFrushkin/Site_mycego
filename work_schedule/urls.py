from django.urls import path

from .views import WorkSchedule

app_name = 'work'

urlpatterns = [
    path('', WorkSchedule.as_view(), name='work_page'),
]
