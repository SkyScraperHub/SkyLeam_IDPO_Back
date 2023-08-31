from django.db.models import Q
from django.contrib import admin

class SingleDateFilter(admin.SimpleListFilter):
    title = _('Дата')
    parameter_name = 'date_field'

    def lookups(self, request, model_admin):
        """
        Здесь вы можете изменить метод, чтобы он возвращал список дат, по 
        которому можно осуществить фильтрацию, или изменить его для получения 
        ввода от пользователя. Возвращаемый кортеж должен содержать первым 
        элементом закодированное значение для опции, которое появится в строке 
        запроса URL. Второй элемент - это удобочитаемое название для опции, 
        которое появится в правой боковой панели.
        """
        return (
            # TODO: Configure your choice of dates or implement user input.
        )

    def queryset(self, request, queryset):
        """
        Возвращает отфильтрованный queryset на основе значения, предоставленного 
        в строке запроса, которое можно получить через `self.value()`.
        """
        if self.value():
            # Change 'date_field' to your date field.
            return queryset.filter(date_field__date=self.value())
        else:
            return queryset