from django.contrib import admin
from django.http import HttpResponse
from .models import Session
from user.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.http import urlencode
import pandas as pd
from django.db.models import Q
from datetime import datetime
from filters import MyDateRangeFilter, ScenarioFilter, IdFilter
from utils import convert_id_int_to_str
# Register your models here.

class SessionTabular(Session):
    class Meta:
        proxy = True
        
class SessionModelInline(admin.TabularInline):
    model = SessionTabular
    fields = ("object_id", "date_correct", "time_correct", "scenario", "report", "video_url")
    readonly_fields = ("object_id", "date_correct", "time_correct", "scenario", "report", "video_url")
    model._meta.verbose_name_plural = _("Сессии тренажеров")
    
    def object_id(self, obj):
        return convert_id_int_to_str(obj.id)
    
    object_id.short_description = "ID"
    
    def date_correct(self, obj):
        return obj.date.strftime('%d-%m-%Y')
    
    def time_correct(self, obj):
        return str(obj.time)
    
    def report(self, obj):
        url = (
            reverse("doc-generate")\
            + "?"\
            + urlencode({"pk":f"{obj.id}"})
        )
        highlighted_text = f"<a href={url} target='_blank' download>Скачать отчет</a>"
        return format_html(highlighted_text)
    
    def video_url(self, obj):
        url = reverse("session-video", args=[obj.id])
        # highlighted_text = f"<a href='{url}' target='_blank' onclick='window.open(`{url}`, `_blank`)'>Просмотреть видео</a>"
        highlighted_text = f"<a href='{url}' target='_blank'>Просмотреть видео</a>"
        return format_html(highlighted_text)
    
    report.short_description = "Файл отчет"
    
    video_url.short_description = "Видеоматериал"
    
    object_id.short_description = "ID"
    
    date_correct.short_description = "Дата"
    
    time_correct.short_description = "Время"   
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    
class SessionProxyAdmin(Session):
    class Meta:
        proxy = True
        verbose_name = _("сессию")
        verbose_name_plural = _("Коллекции Сессий")
    def __str__ (self):
        return ""
    
@admin.register(SessionProxyAdmin)
class SessionAdmin(admin.ModelAdmin):
    
    list_filter = (('date', MyDateRangeFilter),("id", IdFilter), ("scenario", ScenarioFilter),)
    
    ordering = ("id", )
    
    actions = ["get_session_report"]
    
    @admin.action(description="Выгрузить файл-отчет сессий")
    def get_session_report(self,request,queryset):
        excelOutput = []
        for obj in queryset:
            user = User.objects.get(id=obj.FK_user_id)
            full_name = user.last_name+" " + user.first_name +" "+ user.middle_name

            excelOutput.append([full_name, obj.date.strftime('%d-%m-%Y'), str(obj.time), obj.scenario, (str(obj.result)+"%")])

        df = pd.DataFrame(excelOutput,columns=["Фамилия И.О.","Дата","Время","Сценарий","Результат"])
        response = HttpResponse( content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Otchet po sessiam {datetime.now().strftime("%Y.%m.%d")}.xlsx"'
        df.to_excel(response, index=False)
        # messages.add_message(request, messages.INFO, 'Перезагрузите страницу, чтобы увидеть обновления.')
        return response
    
    def object_id(self, obj):
        user = User.objects.get(id=obj.FK_user_id)
        url = (
            reverse(f"admin:user_userstudent_change",args=[user.id])
        )
        return format_html('<a href="{}">{} </a>', url, convert_id_int_to_str(obj.FK_user_id))
    
    object_id.short_description = "ID курсанта"
    
    def date_correct(self, obj):
        return obj.date.strftime('%d-%m-%Y')
    
    date_correct.short_description = "Дата"
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def report(self, obj):
        url = (
            reverse("doc-generate")\
            + "?"\
            + urlencode({"pk":f"{obj.id}"})
        )
        highlighted_text = f"<a href={url} target='_blank' download>Скачать отчет</a>"
        return format_html(highlighted_text)
    
    report.short_description = "Файл отчет"
    
    def time_correct(self, obj):
        return str(obj.time)
    
    time_correct.short_description = "Время"
    
    def full_name(self, obj):
        user = User.objects.get(id = obj.FK_user_id)
        return user.last_name+" " + user.first_name +" "+ user.middle_name
    
    full_name.short_description = "Фамилия И.О."
    
    def rank(self, obj):
        return obj.FK_user.rank
    
    def get_list_display(self, request):
         return ('object_id', "full_name", 'date_correct', 'time_correct', 'scenario', "report")
     
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.position ==  User.POSITION_CHOICES[0][0]: 
            students = User.objects.filter(fk_user=request.user.id).values_list("id", flat=True)
            return qs.filter(Q(FK_user_id__in=students))
        return qs