from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
class Is_ActiveFilter(admin.SimpleListFilter):
    title = _('Статус')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('True', _('Разблокированный')),
            ('False', _('Заблокированный')),  
        )
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(is_active=self.value())
        else:
            return queryset
        
class Is_OlderThan6Months(admin.SimpleListFilter):
    title = _('Время подключения')
    parameter_name = 'date_joined'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("Bigger", _('Больше 6 месяцев')),
            ('Smaller', _('Меньше 6 месяцев')), 
        )
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        Time = datetime.datetime.now() - relativedelta(months=6)
        if self.value() == "Bigger":
            # smallerTime = datetime.datetime.now() - relativedelta(months=6)
            return queryset.filter(date_joined__lte=Time)
        elif self.value() == "Smaller":
            # smallerTime = datetime.datetime.now() - relativedelta(months=6)
            return queryset.filter(date_joined__gte=Time)
        
# class IsTest(admin.SimpleListFilter):
#     title = _('Дата оплаты')
#     parameter_name = 'next_payment_time'

#     def lookups(self, request, model_admin):
#         return (
#             ('closest', 'Ближайший'),
#             # ('furthest', 'Самый дальний'),
#         )

#     def queryset(self, request, queryset):
#         if self.value() == 'closest':
#             # Здесь реализуйте получение параметра next_payment_time, если он требует вычисления.
#             # Затем используйте аннотацию для добавления поля next_payment_time к queryset.
#             queryset = queryset.annotate(
#                 next_payment_time=ExpressionWrapper(F("subscription_start_time") - timedelta(days=30))
#             )
#             return queryset.order_by('next_payment_time')

#         # if self.value() == 'furthest':
#         #     # Здесь реализуйте получение параметра next_payment_time, если он требует вычисления.
#         #     # Затем используйте аннотацию для добавления поля next_payment_time к queryset.
#         #     queryset = queryset.annotate(
#         #         next_payment_time=ExpressionWrapper(Пример выражения)
#         #     )
#         #     return queryset.order_by('-next_payment_time')
