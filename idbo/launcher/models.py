from typing import Any
from django.db import models
from django.forms import ValidationError
from user.models import User
from django.utils import timezone
from datetime import time
from services.s3 import MinioClient
import os
from utils import upload_to
# Создаем модель "Сессия"
class Session(models.Model):
    # Уникальный идентификатор сессии
    id = models.AutoField(primary_key=True)

    # Внешний ключ, связывающий сессию с пользователем
    FK_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    # Дата сессии
    date = models.DateField(default=timezone.now, verbose_name='Дата')

    # Время начала сессии
    time = models.TimeField(default=time.min, verbose_name='Время')

    # Описание сценария
    scenario = models.TextField(verbose_name='Сценарий')

    # Результат сессии (целое число)
    result = models.IntegerField(verbose_name='Результат')

    video = models.TextField(max_length=30, verbose_name="Название видео")

    def __str__(self):
        return f" "
    
    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object("/" + str(self.FK_user.id) + "/" + self.video)
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(Session, self).delete(*args, **kwargs)

def validate_file_extension( value):
    ext = value.name.split(".")[-1]  # Получаем расширение файла
    valid_extensions = ['zip']  # Допустимые расширения
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'Поддерживается следующий формат файла:{",".join(valid_extensions)}')
    
class Game(models.Model):
    # Уникальный идентификатор сессии
    id = models.AutoField(primary_key=True, unique=True, auto_created=True)

    # Внешний ключ, связывающий сессию с пользователем
    name = models.TextField(verbose_name = "Название")
    file = models.FileField(upload_to=upload_to, verbose_name="Архив", default=None, validators=[validate_file_extension, ])
    exe_name = models.TextField(verbose_name="Имя файла")

    
    def __str__(self):
        return f" "
    
    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object("/" +self.id +".zip")
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(Session, self).delete(*args, **kwargs)


class GameImage(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.ImageField(upload_to=upload_to,null=False, verbose_name="Название файла запуска")
    game_id = models.ForeignKey("game", on_delete=models.CASCADE, verbose_name="Изображение")

    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object("/" +self.game_id.id +"/"+self.file_name)
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(GameImage, self).delete(*args, **kwargs)
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'