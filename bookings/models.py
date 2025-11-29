from django.db import models
from django.conf import settings

class Room(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название/Номер")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

    def __str__(self):
        return f'{self.name} (до {self.capacity} чел.)'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('canceled', 'Отменено'),
    ]
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='bookings', 
        verbose_name='Комната'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings', 
        verbose_name='Пользователь'
    )
    
    start_time = models.DateTimeField(verbose_name="Начало бронирования")
    end_time = models.DateTimeField(verbose_name="Конец бронирования")
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active', 
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at'] 

    def __str__(self):
        return f'{self.room.name} — {self.start_time.strftime("%d.%m %H:%M")}'