from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from .models import Session, Game, GameImage
from user.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.http import urlencode
import pandas as pd
import os, uuid
from services.s3 import MinioClient
from django.db.models import Q
from services.s3 import MinioClient
from datetime import datetime
from filters import MyDateRangeFilter, ScenarioFilter, IdFilter
from utils import convert_id_int_to_str
# Register your models here.

class GameImageAdmin(admin.StackedInline):
    model = GameImage
    
    extra =0
    def get_image_html(self, obj):
        return format_html('<img src="{}" style="max-height:200px;"/>'.format(obj.img.url))

    get_image_html.short_description = "Изображение"
    readonly_fields = ('get_image_html',)
    
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
    
class GameProxyAdmin(Game):
    class Meta:
        proxy = True
        verbose_name = _("тренажер")
        verbose_name_plural = _("Коллекции Тренажеров")
    def __str__(self):
        return  ""
    
@admin.register(GameProxyAdmin)
class GameAdmin(admin.ModelAdmin):
    
    # form = AdminAdminForm
    inlines = [GameImageAdmin]
    ordering = ("id", )
    
    actions = ['delete_selected']
    
    def delete_selected(self, request, queryset):
        self.model._meta.verbose_name = "Тренажер"
        # Implement your custom deletion logic here

        # This could be directly deleting the objects
        for obj in queryset:
            obj.delete()
    delete_selected.short_description = "Удалить выбранные тренажеры"
    fieldsets = (
        (None, {'fields': ("name", "exe_name", "description", "file" ),}),
    )
    
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
        extra_context["history"] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    # def has_view_permission(self, request, obj=None) -> bool:
    #     if request.user.position != User.POSITION_CHOICES[2][0]:
    #         return False
    #     return True
    
    def has_change_permission(self, request, obj=None):
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True
    
    def download_obj_button(self, obj):

        highlighted_text = f"<a href={obj.file.url} target='_blank' download>Скачать тренажер</a>"
        return format_html(highlighted_text)
    
    download_obj_button.short_description = 'Действие'

    
    def get_list_display(self, request):
         self.model._meta.verbose_name = "тренажера"
         return ("object_id", "name", 'download_obj_button')
    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        # if hasattr(obj, "id"):
        #     game = Game.objects.get(pk = obj.id)
        # else:
        #     pass
        
        # try:
        #     user = User.objects.get(id = obj.id)
        #     if user.profile_image != "" and obj.profile_image == "":
        #         MinioClient.delete_object(user.profile_image.name)
        #     elif user.profile_image != obj.profile_image:
        #         MinioClient.delete_object(user.profile_image.name) 
        # except:
        #     pass
        # self.model._meta.verbose_name = "Пользователь"
        # if 'profile_image' in request.FILES:
        #     image = request.FILES['profile_image']
        #     img_name = get_random_string(40)
        #     img_prefix = image.name.split(".")
        #     img = f"{img_name}.{img_prefix[-1]}"
        #     MinioClient.upload_data(img, image, image.size)
        #     obj.profile_image =  img
        # if obj.position == "":
        #     obj.position = User.POSITION_CHOICES[2][0]
        # try:
        #     if form.initial["password"] != obj.password:
        #         obj.password = make_password(obj.password)
        # except:
        #     obj.password = make_password(obj.password)
        # obj.is_administrator = True
        # obj.is_superuser = True
        # obj.fk_user = None
        # obj.is_staff = True 
        
        super().save_model(request, obj, form, change)
    
    def object_id(self, obj):
        return convert_id_int_to_str(obj.id)
    
    object_id.short_description = "ID"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # form.base_fields['profile_image'].label = ''
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    