from typing import Any, Dict, List, Optional, Tuple
from django.contrib import admin
from django.http.request import HttpRequest
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User
from launcher.admin import SessionModelInline
from .forms import StudentAdminForm, InstructorAdminForm, AdminAdminForm
from django.db.models import Q
from django.contrib.auth.models import Group
from django.views.decorators.clickjacking import xframe_options_exempt
from services.s3 import MinioClient
import os

class UserAdmin(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Коллекции Администраторов")
    def __str__ (self):
        return ""


@admin.register(UserAdmin)
class UserAdminAdmin(admin.ModelAdmin):
    form = AdminAdminForm

    readonly_fields = ['profile_image_preview']

    fieldsets = (
        (None, {'fields': ('profile_image_preview', "profile_image", "last_name", "first_name", "middle_name", "login", "password", "email", "is_active"),}),
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
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def has_view_permission(self, request, obj=None) -> bool:
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True
    
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
    
    def profile_image_preview(self, obj):
        return format_html('<img src="{}" width="150" height="150" />', obj.profile_image.url)
    profile_image_preview.short_description = 'Изображение профиля'
    def full_name(self, obj):
        return obj.middle_name+" " + obj.first_name +" "+ obj.last_name
    
    full_name.short_description = "ФИО"
    
    def get_list_display(self, request):
         return ("object_id", 'last_name', "full_name", 'email', "phone_number", 'position')
    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        if 'profile_image' in request.FILES:
            image = request.FILES['profile_image']
            MinioClient.upload_data(image.name, image, image.size)
            obj.profile_image = os.getenv("MINIO_FOLDER") + "/" + image.name
        if obj.position == "":
            obj.position = User.POSITION_CHOICES[2][0]
        try:
            if form.initial["password"] != obj.password:
                obj.password = make_password(obj.password)
        except:
            obj.password = make_password(obj.password)
        obj.is_administrator = True
        obj.is_superuser = True
        obj.fk_user = None
        obj.is_staff = True 
        
        super().save_model(request, obj, form, change)
    
    def object_id(self, obj):
        return obj.id
    
    object_id.short_description = "ID"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['profile_image'].label = ''
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(position=User.POSITION_CHOICES[2][0]))
    
class UserInstructor(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Коллекции Инструкторов")
    def __str__ (self):
        return ""


class UserStudent(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Коллекции Инструктируемых")
    def __str__ (self):
        return ""

class UserStudentTabular(User):
    class Meta:
        proxy = True
    def __str__ (self):
        return ""
            
class StudentModelInline(admin.TabularInline):
    model = UserStudentTabular
    fields = ("object_id", "full_name", "position")
    readonly_fields = ("object_id", "full_name", "position")
    model._meta.verbose_name_plural = _("Инструктируемые")
    
    def object_id(self, obj):
        url = (
            reverse(f"admin:user_userstudent_change",args=[obj.id])
        )
        return format_html('<a href="{}">{} </a>', url, obj.id)
    
    def full_name(self, obj):
        return obj.last_name+" " + obj.first_name +" "+ obj.middle_name
    
    full_name.short_description = "Фамилия ИО"
    
    object_id.short_description = "ID"
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserInstructor)
class UserInstructorAdmin(admin.ModelAdmin):
    list_display = ( "id", "full_name", "phone_number", "email", "position")
    form = InstructorAdminForm
    inlines = [StudentModelInline,]
    readonly_fields = ['profile_image_preview']
    
    fieldsets = (
        (None, {'fields': ('profile_image_preview', "profile_image", "last_name", "first_name", "middle_name", "login", "password", "email", "phone_number", "is_active"),}),
    )
    
    def full_name(self, obj):
        return obj.last_name+" " + obj.first_name +" "+ obj.middle_name
    
    full_name.short_description = "Фамилия ИО"
    
    def has_view_permission(self, request, obj=None) -> bool:
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True
    
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
    
    def profile_image_preview(self, obj):
        return format_html('<img src="{}" width="150" height="150" />', obj.profile_image.url)
    profile_image_preview.short_description = 'Изображение профиля'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['profile_image'].label = ''
        return form
    
    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        if 'profile_image' in request.FILES:
            image = request.FILES['profile_image']
            MinioClient.upload_data(image.name, image, image.size)
            obj.profile_image = os.getenv("MINIO_FOLDER") + "/" + image.name
        if obj.position == "":
            obj.position = User.POSITION_CHOICES[0][0]
        try:
            if form.initial["password"] != obj.password:
                obj.password = make_password(obj.password)
        except:
            obj.password = make_password(obj.password)
        obj.is_administrator = True
        obj.is_superuser = True
        obj.fk_user = None
        obj.is_staff = True
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(position=User.POSITION_CHOICES[0][0]))

@admin.register(UserStudent)
class UserStudentAdmin(admin.ModelAdmin):

    form = StudentAdminForm
    ordering = ('id', )
    inlines = [SessionModelInline,]
    
    readonly_fields = ['profile_image_preview']
    
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
    
    def profile_image_preview(self, obj):
        return format_html('<img src="{}" width="150" height="150" />', obj.profile_image.url)
    profile_image_preview.short_description = 'Изображение профиля'
    
    def has_delete_permission(self, request, obj=None):
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True
    
    def full_name(self, obj):
        return obj.last_name+" " + obj.first_name +" "+ obj.middle_name
    
    def id_instructor(self, obj):
        return obj.fk_user_id
    
    full_name.short_description = "Фамилия ИО"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and request.user.position != User.POSITION_CHOICES[2][0]:   # This means that obj is not None, so you're in a change view
            return ['profile_image_preview', "profile_image", 'login', 'last_name', 'first_name', 'middle_name', 'phone_number', 'fk_user', 'email', 'is_active']
        else:    # This means you're in an add view
            return ['profile_image_preview']
    
    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...) -> List[Tuple[str | None, Dict[str, Any]]]:
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return (
        (None, {'fields': ('profile_image_preview', "profile_image", "login", "password",  "last_name", "first_name", "middle_name", "phone_number", "email", "is_active"),}),
    )
        return (
        (None, {'fields': ('profile_image_preview', "profile_image", "login", "password",  "last_name", "first_name", "middle_name", "phone_number", "fk_user", "email", "is_active"),}),
    )
    
    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        if 'profile_image' in request.FILES:
            image = request.FILES['profile_image']
            MinioClient.upload_data(image.name, image, image.size)
            obj.profile_image = os.getenv("MINIO_FOLDER") + "/" + image.name
        if obj.position == "":
            obj.position = User.POSITION_CHOICES[1][0]
        try:
            if form.initial["password"] != obj.password:
                obj.password = make_password(obj.password)
        except:
            obj.password = make_password(obj.password)
        if not obj.fk_user_id:
            obj.fk_user_id = request.user.id
            obj.fk_user = User.objects.get(id=request.user.id)
        obj.is_administrator = True
        obj.is_superuser = True
        obj.is_staff = True
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        
        form = super().get_form(request, obj, **kwargs)
        try:
            form.base_fields['profile_image'].label = ''
        except:
            pass
        return form
    
    def get_list_display(self, request):
        if request.user.position == User.POSITION_CHOICES[0][0]:
            return ('id', "full_name", "phone_number", "email", "position")
        return ('id', "full_name", "phone_number", "email", "position","id_instructor")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.position == User.POSITION_CHOICES[0][0]:
            return qs.filter(Q(fk_user=request.user.id) & Q(position=User.POSITION_CHOICES[1][0]))
        return qs.filter(Q(position=User.POSITION_CHOICES[1][0]))


admin.site.unregister(Group)
