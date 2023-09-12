from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from users.forms import UserLoginForm, CustomUserEditForm, UserProfileEditForm


class UserLogin(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'
    redirect_authenticated_user = 'main_site:main_site'

    def form_valid(self, form):
        # Проверяем work_status пользователя
        user = form.get_user()
        if user.status_work:
            return super().form_valid(form)
        else:
            # Если work_status равно False, перенаправляем пользователя обратно на страницу входа
            return HttpResponseRedirect(reverse_lazy('users:login'))


class UserLogout(LogoutView):
    template_name = 'user/login.html'


class ProfileView(View):
    template_name = 'user/profile.html'

    def get(self, request):
        return render(request, self.template_name)


class EditProfileView(View):
    template_name = 'user/edit_profile.html'

    def get(self, request):
        form = UserProfileEditForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})
