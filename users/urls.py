from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetConfirmView,
    PasswordResetCompleteView, PasswordResetDoneView, PasswordChangeView, PasswordChangeDoneView
)
from .views import UserLogout, UserLogin, ProfileView, EditProfileView, Staff, user_profile

app_name = 'users'

urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('staff/', Staff.as_view(), name='staff'),
    path('profile_user/<int:user_id>/', user_profile, name='user_profile'),

    # Добавьте следующие URL-шаблоны для сброса пароля
    path('password_reset/', PasswordResetView.as_view(success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(success_url=reverse_lazy('users:login')),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Добавьте следующие URL-шаблоны для смены пароля
    path('password_change/', PasswordChangeView.as_view(success_url=reverse_lazy('users:login')),
         name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
]
