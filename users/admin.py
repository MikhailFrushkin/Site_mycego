from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Role, Department


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('id', 'username', 'avg_kf', 'role', 'status_work', 'updated_at')

    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('role', 'department', 'status_work', 'photo', 'phone_number',
                                        'telegram_id', 'card_details', 'birth_date', 'hobbies', 'nick')}),
        ('Избранные', {'fields': ('favorites',)}),  # Добавляем поле favorites в админку
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'department', 'status_work'),
        }),
    )
    search_fields = ('username',)


class AdminRole(admin.ModelAdmin):
    list_display = [field.name for field in Role._meta.fields]
    list_editable = ['name', 'salary', 'type_salary', 'type_salary2', 'calc_kf', 'order_by']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role, AdminRole)


class AdminDepartment(admin.ModelAdmin):
    list_display = [field.name for field in Department._meta.fields]
    list_display_links = ('name',)


admin.site.register(Department, AdminDepartment)
