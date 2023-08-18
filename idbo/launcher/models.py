from django.db import models
from user.models import User
from django.utils import timezone
from datetime import time

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
        return f"Сессия {self.id} для {self.FK_user} ({self.date} {self.time})"
