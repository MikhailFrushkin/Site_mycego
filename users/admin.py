from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Role


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('id', 'username', 'role', 'status_work')

    fieldsets = UserAdmin.fieldsets + (
        ('Доп. инофрмация', {'fields': ('role', 'status_work', 'photo', 'phone_number',
                                        'telegram_id', 'card_details', 'birth_date', 'hobbies')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status_work'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
