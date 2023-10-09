from django.urls import path

from .views import Effectiveness, StatisticView, StatisticWorks

app_name = 'effectiveness'

urlpatterns = [
    path('', Effectiveness.as_view(), name='effectiveness'),
    path('statistic/', StatisticView.as_view(), name='effectiveness_statistic'),
    path('statistic_works/', StatisticWorks.as_view(), name='statistic_works'),

]