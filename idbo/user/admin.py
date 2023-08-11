from django.contrib import admin
from django.utils.translation import gettext_lazy as _


from .models import User



# Создаем админский класс для модели User
class UserAdmin(User):
    class Meta:
        proxy=True
@admin.register(UserAdmin)
class CustomUserAdmin(admin.ModelAdmin):
    model = UserAdmin
    list_display = ('last_name', 'first_name', 'email', 'position', 'is_administrator', 'is_active')
    list_filter = ('position', 'is_administrator', 'is_active')
    # fieldsets = (
    #     (None, {'fields': ('last_name', 'first_name', 'middle_name', 'phone_number', 'email', 'login', 'password', 'fk_user', 'position', 'is_administrator', 'image_field')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    # )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('last_name', 'first_name', 'middle_name', 'phone_number', 'email', 'login', 'password1', 'password2', 'position', 'is_administrator', 'is_active')}
    #     ),
    # )
    search_fields = ('last_name', 'first_name', 'midle_name', 'phone_number', 'email', 'login')
    ordering = ('last_name', 'first_name')
