from django.urls import path

from .views import DownloadFiles

app_name = 'download'

urlpatterns = [
    path('', DownloadFiles.as_view(), name='download'),
    # path('edit_work/', EditWork.as_view(), name='download'),
]
