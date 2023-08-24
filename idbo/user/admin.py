from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User
from launcher.admin import SessionModelInline
from .forms import StudentAdminForm, InstructorAdminForm, AdminAdminForm
from django.db.models import Q
from django.contrib.auth.models import Group
from django.views.decorators.clickjacking import xframe_options_exempt
from services.s3 import MinioClient


class UserAdmin(User):
    class Meta:
        proxy = True
        
    def __str__ (self):
        return ""


@admin.register(UserAdmin)
class CustomUserAdmin(admin.ModelAdmin):
    model = UserAdmin
    form = AdminAdminForm
    list_display = ('last_name', "full_name" ,'first_name', 'email', 'position', 'profile_image_tag')

    def full_name(self, obj):
        return obj.middle_name+" " + obj.first_name +" "+ obj.last_name
    
    full_name.short_description = "ФИО"
    
    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        if 'profile_image' in request.FILES:
            image = request.FILES['profile_image']
            MinioClient.upload_data(image.name, image.read(), image.size)
            obj.profile_image = image.name
        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['profile_image'].label = 'Изображение профиля'
        return form
    
class UserInstructor(User):
    class Meta:
        proxy = True
    
    def __str__ (self):
        return ""


class UserStudent(User):
    class Meta:
        proxy = True
        verbose_name = _("объект")
        verbose_name_plural = _("Коллекция Инструктируемых")
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
    list_display = ( "id","phone_number", "email", "position")
    model = UserInstructor
    model._meta.verbose_name = _("объект")
    model._meta.verbose_name_plural = _("Коллекция Инструкторов")
    form = InstructorAdminForm
    inlines = [StudentModelInline,]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(position=User.POSITION_CHOICES[0][0]))


@admin.register(UserStudent)
class UserStudentAdmin(admin.ModelAdmin):

    form = StudentAdminForm
    ordering = ('id', )
    inlines = [SessionModelInline,]
    
    def full_name(self, obj):
        return obj.last_name+" " + obj.first_name +" "+ obj.middle_name
    
    def id_instructor(self, obj):
        return obj.fk_user_id
    
    full_name.short_description = "Фамилия ИО"
    
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
