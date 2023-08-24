from django.db import models
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from services.s3 import MinioClient

# Создаем модель пользователя, наследуясь от AbstractBaseUser и PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    # Выбор вариантов для поля "Должность"
    POSITION_CHOICES = (
        ('instructor', 'Инструктор'),
        ('student', 'Обучающийся'),
        ('admin', 'Администратор'),
    )

    # Поле для уникального идентификатора пользователя
    id = models.AutoField(primary_key=True, auto_created=True)

    # Фамилия пользователя
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')

    # Имя пользователя
    first_name = models.CharField(max_length=100, verbose_name='Имя')

    # Отчество пользователя
    middle_name = models.CharField(max_length=100, verbose_name='Отчество')

    # Номер телефона пользователя
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')

    # Email пользователя (уникальный)
    email = models.EmailField(verbose_name='Почта', unique=True)

    # Логин пользователя (уникальный)
    login = models.CharField(max_length=100, unique=True, verbose_name='Логин')

    # Хэшированный пароль пользователя
    password = models.CharField(max_length=128, verbose_name='Пароль')

    # Внешний ключ на родительского пользователя (связь с самим собой)
    fk_user = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, verbose_name='Родительский пользователь')

    # Выбор должности пользователя из списка POSITION_CHOICES
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='Должность')

    # Флаг, указывающий, является ли пользователь администратором
    is_administrator = models.BooleanField(default=False, verbose_name='Администратор')
    
    # Флаг активности пользователя
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    
    is_staff = models.BooleanField(default=True)

    # Дата и время присоединения пользователя
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='Изображение')

    # Имя поля, используемое для аутентификации (логин)
    USERNAME_FIELD = 'login'
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"
    
    
    
    objects = CustomUserManager()
