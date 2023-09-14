from django.urls import path

from .views import Effectiveness, StatisticView

app_name = 'effectiveness'

urlpatterns = [
    path('', Effectiveness.as_view(), name='effectiveness'),
    path('statistic/', StatisticView.as_view(), name='effectiveness_statistic'),

]