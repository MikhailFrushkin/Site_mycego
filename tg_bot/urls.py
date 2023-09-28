from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем роутер для автоматического создания URL-маршрутов для наших представлений
router = DefaultRouter()
# router.register(r'items', views.UserViewSet)
app_name = 'tg_bot'

urlpatterns = [
    # path('', views.UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='other-view'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('appointment/', views.AppointmentView.as_view(), name='appointment-list-by-date'),
    path('appointment_delete/', views.AppointmentDelete.as_view(), name='appointment_delete'),
    path('get_works/', views.WorksList.as_view(), name='get_works'),
    path('add_works/', views.AddWorksList.as_view(), name='add_works'),
    path('view_works/', views.ViewWorks.as_view(), name='view_works'),
    path('view_detail_work/', views.ViewDetailsWorks.as_view(), name='view_detail_work'),
]
