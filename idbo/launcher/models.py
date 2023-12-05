from django.db import models
from user.models import User
from django.utils import timezone
from datetime import time
from services.s3 import MinioClient
import os
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

class Game(models.Model):
    # Уникальный идентификатор сессии
    id = models.AutoField(primary_key=True)

    # Внешний ключ, связывающий сессию с пользователем
    name = models.TextField(verbose_name = "Название")
    
    file_name = models.TextField(verbose_name="Имя файла")

    
    def __str__(self):
        return f" "
    
    def delete(self, *args, **kwargs):
        try:
            MinioClient.delete_object("/" +self.id +"/"+self.file_name)
        # перед удалением, удаляем видео с сервера
        except:
            print("Video don't exist")
        super(Session, self).delete(*args, **kwargs)
