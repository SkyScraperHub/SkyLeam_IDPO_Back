from typing import Any, Dict, List, Tuple
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
from services.s3 import MinioClient
from utils import get_random_string
from django.contrib import admin
from filters import MyDateRangeFilter, IdFilter, FIOFilter
from utils import convert_id_int_to_str

admin.site.site_header = "Панель инструкторов"

admin.site.site_title = "Панель инструкторов"

admin.site.index_title = "Добро пожаловать в панель инструктора!"


class UserAdmin(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Картотеки Администраторов")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


@admin.register(UserAdmin)
class UserAdminAdmin(admin.ModelAdmin):
    form = AdminAdminForm

    list_filter = (
        ("date_joined", MyDateRangeFilter),
        ("id", IdFilter),
        ("full_name", FIOFilter),
    )

    ordering = ("id",)

    readonly_fields = ["profile_image_preview"]

    actions = ["delete_selected"]

    def delete_selected(self, request, queryset):
        self.model._meta.verbose_name = "Пользователь"
        # Implement your custom deletion logic here

        # This could be directly deleting the objects
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Удалить выбранных пользователей"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "profile_image_preview",
                    "profile_image",
                    "login",
                    "password",
                    "last_name",
                    "first_name",
                    "middle_name",
                    "rank",
                    "phone_number",
                    "email",
                    "is_active",
                ),
            },
        ),
    )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        extra_context["history"] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

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
        return format_html(
            '<img src="{}" width="150" height="150" />', obj.profile_image.url
        )

    profile_image_preview.short_description = "Изображение профиля"

    def full_name(self, obj):
        return obj.last_name + " " + obj.first_name + " " + obj.middle_name

    full_name.short_description = "ФИО"

    def get_list_display(self, request):
        self.model._meta.verbose_name = "пользователя"
        return ("object_id", "full_name", "rank", "email", "phone_number", "position")

    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        try:
            user = User.objects.get(id=obj.id)
            if user.profile_image != "" and obj.profile_image == "":
                MinioClient.delete_object(user.profile_image.name)
            elif user.profile_image != obj.profile_image:
                MinioClient.delete_object(user.profile_image.name)
        except:
            pass
        self.model._meta.verbose_name = "Пользователь"
        if "profile_image" in request.FILES:
            image = request.FILES["profile_image"]
            img_name = get_random_string(40)
            img_prefix = image.name.split(".")
            img = f"{img_name}.{img_prefix[-1]}"
            MinioClient.upload_data(img, image, image.size)
            obj.profile_image = img
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
        return convert_id_int_to_str(obj.id)

    object_id.short_description = "ID"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["profile_image"].label = ""
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(position=User.POSITION_CHOICES[2][0]))


class UserInstructor(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Картотеки Инструкторов")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class UserStudent(User):
    class Meta:
        proxy = True
        verbose_name = _("пользователя")
        verbose_name_plural = _("Картотеки Курсантов")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class UserStudentTabular(User):
    class Meta:
        proxy = True

    def __str__(self):
        return ""


class StudentModelInline(admin.TabularInline):
    model = UserStudentTabular
    fields = ("object_id", "full_name", "position")
    readonly_fields = ("object_id", "full_name", "position")
    model._meta.verbose_name_plural = _("Инструктируемые")

    def object_id(self, obj):
        url = reverse(f"admin:user_userstudent_change", args=[obj.id])
        return format_html('<a href="{}">{} </a>', url, obj.id)

    def full_name(self, obj):
        return obj.last_name + " " + obj.first_name + " " + obj.middle_name

    full_name.short_description = "Фамилия И.О."

    object_id.short_description = "ID"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserInstructor)
class UserInstructorAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_filter = (
        ("date_joined", MyDateRangeFilter),
        ("id", IdFilter),
        ("full_name", FIOFilter),
    )
    form = InstructorAdminForm
    inlines = [
        StudentModelInline,
    ]
    readonly_fields = ["profile_image_preview"]
    actions = ["delete_selected"]

    def delete_selected(self, request, queryset):
        self.model._meta.verbose_name = "Пользователь"
        # Implement your custom deletion logic here

        # This could be directly deleting the objects
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Удалить выбранных пользователей"

    def object_id(self, obj):
        return convert_id_int_to_str(obj.id)

    object_id.short_description = "ID"

    def get_list_display(self, request):
        self.model._meta.verbose_name = "пользователя"
        return ("object_id", "full_name", "rank", "phone_number", "email", "position")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "profile_image_preview",
                    "profile_image",
                    "login",
                    "password",
                    "last_name",
                    "first_name",
                    "middle_name",
                    "rank",
                    "phone_number",
                    "email",
                    "is_active",
                ),
            },
        ),
    )

    def full_name(self, obj):
        return obj.last_name + " " + obj.first_name + " " + obj.middle_name

    full_name.short_description = "Фамилия И.О."

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

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def profile_image_preview(self, obj):
        return format_html(
            '<img src="{}" width="150" height="150" />', obj.profile_image.url
        )

    profile_image_preview.short_description = "Изображение профиля"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["profile_image"].label = ""
        return form

    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        try:
            user = User.objects.get(id=obj.id)
            if user.profile_image != "" and obj.profile_image == "":
                MinioClient.delete_object(user.profile_image.name)
            elif user.profile_image != obj.profile_image:
                MinioClient.delete_object(user.profile_image.name)
        except:
            pass
        self.model._meta.verbose_name = "Пользователь"
        if "profile_image" in request.FILES:
            image = request.FILES["profile_image"]
            folder = get_random_string(40)
            MinioClient.upload_data(f"{folder}/{image.name}", image, image.size)
            obj.profile_image = f"{folder}/{image.name}"
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
    ordering = ("id",)
    inlines = [
        SessionModelInline,
    ]
    list_filter = (
        ("date_joined", MyDateRangeFilter),
        ("id", IdFilter),
        ("full_name", FIOFilter),
    )
    # search_fields = ["id",]
    readonly_fields = [
        "instructor",
    ]
    actions = ["delete_selected"]

    def delete_selected(self, request, queryset):
        self.model._meta.verbose_name = "Пользователь"
        # Implement your custom deletion logic here

        # This could be directly deleting the objects
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Удалить выбранных пользователей"

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def profile_image_preview(self, obj):
        return format_html(
            '<img src="{}" width="150" height="150" />', obj.profile_image.url
        )

    profile_image_preview.short_description = "Изображение профиля"

    def has_delete_permission(self, request, obj=None):
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return False
        return True

    def object_id(self, obj):
        return convert_id_int_to_str(obj.id)

    object_id.short_description = "ID"

    def full_name(self, obj):
        return obj.last_name + " " + obj.first_name + " " + obj.middle_name

    def instructor(self, obj):
        if obj.fk_user_id is None:
            return ""
        url = reverse(f"admin:user_userinstructor_change", args=[obj.fk_user_id])
        return format_html(
            '<a href="{}">{} </a>', url, convert_id_int_to_str(obj.fk_user_id)
        )

    instructor.short_description = "ID инструктора"
    full_name.short_description = "Фамилия И.О."

    def get_readonly_fields(self, request, obj=None):
        if (
            obj and request.user.position != User.POSITION_CHOICES[2][0]
        ):  # This means that obj is not None, so you're in a change view
            return [
                "profile_image_preview",
                "profile_image",
                "login",
                "last_name",
                "first_name",
                "middle_name",
                "phone_number",
                "email",
                "instructor",
                "fk_user",
                "rank",
            ]
        else:  # This means you're in an add view
            return [
                "profile_image_preview",
                "instructor",
            ]

    def get_fieldsets(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> List[Tuple[str | None, Dict[str, Any]]]:
        if request.user.position != User.POSITION_CHOICES[2][0]:
            return (
                (
                    None,
                    {
                        "fields": (
                            "profile_image_preview",
                            "login",
                            "password",
                            "last_name",
                            "first_name",
                            "middle_name",
                            "rank",
                            "phone_number",
                            "email",
                            "is_active",
                        ),
                    },
                ),
            )
        return (
            (
                None,
                {
                    "fields": (
                        "profile_image_preview",
                        "profile_image",
                        "login",
                        "password",
                        "last_name",
                        "first_name",
                        "middle_name",
                        "rank",
                        "phone_number",
                        "email",
                        "instructor",
                        "fk_user",
                        "is_active",
                    ),
                },
            ),
        )

    def save_model(self, request, obj, form, change):
        # Загрузка изображения на S3
        try:
            user = User.objects.get(id=obj.id)
            if user.profile_image != "" and obj.profile_image == "":
                MinioClient.delete_object(user.profile_image.name)
            elif user.profile_image != obj.profile_image:
                MinioClient.delete_object(user.profile_image.name)
        except:
            pass
        self.model._meta.verbose_name = "Пользователь"
        if "profile_image" in request.FILES:
            image = request.FILES["profile_image"]
            folder = get_random_string(40)
            MinioClient.upload_data(f"{folder}/{image.name}", image, image.size)
            obj.profile_image = f"{folder}/{image.name}"
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
        obj.is_administrator = False
        obj.is_superuser = False
        obj.is_staff = False
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # try:
        #     form.base_fields['profile_image'].label = ''
        #     # form.base_fileds["profile_image"].initial_text = ""
        # except:
        #     pass
        return form

    def get_list_display(self, request):
        self.model._meta.verbose_name = "пользователя"
        if request.user.position == User.POSITION_CHOICES[0][0]:
            return (
                "object_id",
                "full_name",
                "rank",
                "phone_number",
                "email",
                "position",
            )
        return (
            "object_id",
            "full_name",
            "rank",
            "phone_number",
            "email",
            "position",
            "instructor",
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.position == User.POSITION_CHOICES[0][0]:
            return qs.filter(
                Q(fk_user=request.user.id) & Q(position=User.POSITION_CHOICES[1][0])
            )
        return qs.filter(Q(position=User.POSITION_CHOICES[1][0]))


admin.site.unregister(Group)
