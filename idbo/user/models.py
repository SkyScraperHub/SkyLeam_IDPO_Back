from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Создаем модель пользователя, наследуясь от AbstractBaseUser и PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    # Выбор вариантов для поля "Должность"
    POSITION_CHOICES = (
        ('instructor', 'Инструктор'),
        ('student', 'Обучающийся'),
        ('admin', 'Администратор'),
    )

    # Поле для уникального идентификатора пользователя
    id = models.AutoField(primary_key=True)

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
    fk_user = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, verbose_name='Родительский пользователь')

    # Выбор должности пользователя из списка POSITION_CHOICES
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='Должность')

    # Флаг, указывающий, является ли пользователь администратором
    is_administrator = models.BooleanField(default=False, verbose_name='Администратор')
    
    # Флаг активности пользователя
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    # Дата и время присоединения пользователя
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    # Имя поля, используемое для аутентификации (логин)
    USERNAME_FIELD = 'login'

    # Список дополнительных полей, которые будут запрашиваться при создании пользователя
    REQUIRED_FIELDS = ['last_name', 'first_name', 'email']

    # Метод для представления пользователя в виде строки
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.login})"
