from typing import Any
from django.db import models
from django.forms import ValidationError
from user.models import User
from django.utils import timezone
from datetime import time
from services.s3 import MinioClient
import os, re
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
    valid_extensions = ['zip', 'rar']  # Допустимые расширения
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'Поддерживается следующий формат файла:{",".join(valid_extensions)}')
def validate_version_format(value):
    pattern = re.compile(r'^\d+\.\d+\.\d+$')
    if not pattern.match(value):
        raise ValidationError('%(value)s is not a valid version format', params={'value': value})

class Game(models.Model):
    # Уникальный идентификатор сессии
    id = models.AutoField(primary_key=True, unique=True, auto_created=True)

    # Внешний ключ, связывающий сессию с пользователем
    name = models.CharField(max_length=100, verbose_name = "Название")
    file = models.FileField( upload_to=upload_to, verbose_name="Архив", default=None, validators=[validate_file_extension, ])
    exe_name = models.CharField(max_length=100, verbose_name="Имя exe файла")
    description = models.TextField(verbose_name="Описание", default="",null=True)
    version = models.CharField(max_length=100, verbose_name="Версия", validators=[validate_version_format,], null=False, default="0.0.1" )
    use_tcp = models.BooleanField(default=False, verbose_name="Использовать TCP?")
    
    def __str__(self):
        return f" "
    
    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object(f"game/{self.file.name}")
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(Game, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        # Ваша кастомная логика перед сохранением
        # Например, изменение атрибутов
        # if self.id:
        #     file = Game.objects.get(pk=self.id).file
        #     MinioClient.delete_object(file.name)
        # else:
        #     MinioClient.upload_data(f"/game/{self.file.name}", self.file.file, self.file.size, num_parallel_uploads=30)
        # Вызов оригинального метода save
        super(Game, self).save(*args, **kwargs)


class GameImage(models.Model):
    id = models.AutoField(primary_key=True)
    img = models.ImageField(upload_to=upload_to,null=False, verbose_name="Название файла запуска")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images', verbose_name="Изображение")

    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object("/" +self.game_id.id +"/"+self.img.name)
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(GameImage, self).delete(*args, **kwargs)
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
    
    def save(self, *args, **kwargs):
        # Ваша кастомная логика перед сохранением
        # Например, изменение атрибутов
        if self.id:
            img = GameImage.objects.get(pk=self.id).img
            MinioClient.delete_object(img.name)
            
        # Вызов оригинального метода save
        super(GameImage, self).save(*args, **kwargs)
    
    def __str__(self):
        # Вы можете изменить это на любое поле или комбинацию полей вашей модели
        return f""