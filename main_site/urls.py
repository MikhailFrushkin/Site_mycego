from django.urls import path
from .views import MainPage

app_name = 'main_site'

urlpatterns = [
    path('', MainPage.as_view(), name='main_site'),
]
