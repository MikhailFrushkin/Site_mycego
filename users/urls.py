from django.urls import path

from .views import UserLogout, UserLogin, ProfileView, EditProfileView, Staff, user_profile

app_name = 'users'

urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('staff/', Staff.as_view(), name='staff'),
    path('profile_user/<int:user_id>/', user_profile, name='user_profile'),

]
