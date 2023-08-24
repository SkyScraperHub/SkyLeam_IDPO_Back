from django.contrib import admin
from .models import Session
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
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
        return obj.id
    def date_correct(self, obj):
        return obj.date.strftime('%d-%m-%Y')
    
    def time_correct(self, obj):
        return str(obj.time)
    def report(self, obj):
        highlighted_text = f"<a href='http://localhost:8000/api/sessions/report?pk={obj.id}' target='_blank' download>Скачать отчет</a>"
        return format_html(highlighted_text)
    
    def video_url(self, obj):
        return ""
    
    report.short_description = "Файл отчет"
    
    video_url.short_description = "Видеоматериал"
    
    object_id.short_description = "ID"
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False