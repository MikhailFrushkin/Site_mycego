from django.urls import path

from .views import DownloadFiles, DownloadUser

app_name = 'download'

urlpatterns = [
    path('', DownloadFiles.as_view(), name='download'),
    path('download_user/', DownloadUser.as_view(), name='download_user'),
]
