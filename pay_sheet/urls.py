from django.urls import path, reverse_lazy

from pay_sheet.views import PaySheet

app_name = 'pay_sheet'

urlpatterns = [
    path('', PaySheet.as_view(), name='pay_sheet'),

]
