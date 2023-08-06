from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator

import uuid


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        (True, 'Разблокированный'),
        (False, 'Заблокированный')
    )
    IS_ONLY_VIEW_CHOICES = (
        (True, 'Частичный доступ'),
        (False, 'Полный доступ')
    )
    PAYMENT = (("subscription","Подписка"), ("oneGamePay","Оплата за одну сессию"),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list
    email = models.EmailField(verbose_name="Почта",default="")
    login = models.CharField(max_length=100, unique= True, verbose_name="Логин")
    password = models.CharField(max_length=88, verbose_name='Пароль')
    job_title = models.CharField(max_length=100, verbose_name="Отчество")
    admin_type = models.IntegerField()
    
    # data_joined = models.DateTimeField(verbose_name="Дата регистрации", )
    USERNAME_FIELD = 'login'

    #objects = CustomUserManager()