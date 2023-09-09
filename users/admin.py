from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Role


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'role', 'status_work')

    fieldsets = UserAdmin.fieldsets + (
        ('Должность', {'fields': ('role', 'status_work')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status_work'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
