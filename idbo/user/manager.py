from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
class CustomUserManager(BaseUserManager):
    def create_user(self, email, login, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Пользователь должен иметь действительный адрес электронной почты'))
        if not login:
            raise ValueError(_('Пользователь должен иметь логин'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_administrator', True)
        extra_fields.setdefault("position", "admin")
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        return self.create_user(email, login, password, **extra_fields)
