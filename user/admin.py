from django.contrib import admin
from .models import User
from django.contrib import admin
from datetime import datetime
from .forms.user_forms import UserForm
from .admin_filters import Is_ActiveFilter,Is_OlderThan6Months
from datetime import timedelta
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

class UserAbstract(admin.ModelAdmin):
    list_filter = (
        Is_ActiveFilter,
        Is_OlderThan6Months,
    )
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    complete_sessions_time = timedelta(seconds = 900)
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = True
        return super().add_view(request, form_url, extra_context=extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
        
    def has_change_permission(self, request, obj=None):
        return not request.user.is_only_view

    def has_delete_permission(self, request, obj=None):
        return not request.user.is_only_view
    
    def status(self,obj):
        return "Разблокированный" if obj.is_active == True else "Заблокированный"
    
    status.short_description = "Статус"
    


class UserAdmin(User):
    class Meta:
        proxy=True
@admin.register(UserAdmin)
class UserOnePaymentAdmin(UserAbstract):
    list_display = ( "surname",  "name", "patronymic", "phone_number", "email",
                  "login","password","job_title","admin_type",)
    form = UserForm
    model = UserAdmin
    model._meta.verbose_name = _("клиент с единоразовой оплатой")
    model._meta.verbose_name_plural = _("клиенты с единоразовой оплатой")
    title = "Выбирите клиента по подписке для изменения"

    actions = ["comfirm_pay_sessions",]    
  

    @admin.action(description="Отметить как оплаченные и скачать Excel")
    
    
        # messages.add_message(request, messages.SUCCESS, 'Для того, чтобы изменения вступили в силу, пожалуйста обновите страницу.')
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            actions["delete_selected"][0].short_description = "Удалить выбранных клиентов"
        return actions
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Фильтруем пользователей, исключая админа
        return qs.exclude(Q(is_superuser=True) | Q(payment_type='subscription'))
