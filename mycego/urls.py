from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('work/', include('work_schedule.urls', namespace='work')),
    path('completed_works/', include('completed_works.urls', namespace='completed_works')),
    path('effectiveness/', include('effectiveness.urls', namespace='effectiveness')),
    path('pay_sheet/', include('pay_sheet.urls', namespace='pay_sheet')),
    path('download/', include('download_files.urls', namespace='download')),
    path('api-auth/', include('tg_bot.urls', namespace='tg_bot')),
    path('', include('main_site.urls', namespace='main_site')),
]

if settings.DEBUG:
    urlpatterns = [
                      path('__debug__/', include('debug_toolbar.urls')),
                  ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
