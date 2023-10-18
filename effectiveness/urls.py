from django.urls import path

from .views import StatisticViewBad, StatisticWorks, StatisticKfUsers, MainStatisticMenu, StatisticOverWorks

app_name = 'effectiveness'

urlpatterns = [
    path('', MainStatisticMenu.as_view(), name='statistic_main'),
    path('statistic/', StatisticViewBad.as_view(), name='statistic_bad'),
    path('statistic_works/', StatisticWorks.as_view(), name='statistic_works'),
    path('statistic_kf_users/', StatisticKfUsers.as_view(), name='statistic_kf_users'),
    path('statistic_over_works/', StatisticOverWorks.as_view(), name='statistic_over_works'),

]