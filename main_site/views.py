from django.http import HttpResponse
from django.views.generic import ListView, TemplateView
from django.views import View


class MainPage(TemplateView):
    template_name = 'main_page/main.html'
    login_url = '/users/login/'
