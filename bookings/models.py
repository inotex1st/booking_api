from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Room(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Вместимость",
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Создано")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="room_capacity_positive",
            ),
        ]

    def __str__(self):
        return f"{self.name} (до {self.capacity} чел.)"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)


class Booking(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активно"
        CANCELED = "canceled", "Отменено"

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Комната",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь",
    )

    start_time = models.DateTimeField(verbose_name="Начало бронирования")
    end_time = models.DateTimeField(verbose_name="Конец бронирования")

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room", "status", "start_time", "end_time"]),
            models.Index(fields=["user", "status", "start_time"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="booking_end_after_start",
            ),
        ]

    @classmethod
    def overlapping_active(cls, room, start_time, end_time):
        return cls.objects.filter(
            room=room,
            status=cls.Status.ACTIVE,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

    def clean(self):
        errors = {}
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            errors["end_time"] = "Конец бронирования должен быть позже начала."

        if self.start_time and self.status == self.Status.ACTIVE:
            if self.start_time < timezone.now():
                errors["start_time"] = "Нельзя создать активное бронирование в прошлом."

        if self.room_id and self.start_time and self.end_time and self.status == self.Status.ACTIVE:
            overlapping = self.overlapping_active(self.room, self.start_time, self.end_time)
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            if overlapping.exists():
                errors["room"] = "Комната уже забронирована на выбранный интервал."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # проверка на пересечение с другими бронированиями
        self.full_clean()
        return super().save(*args, **kwargs)

    def cancel(self):
        self.status = self.Status.CANCELED
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return f'{self.room.name} - {self.start_time.strftime("%d.%m %H:%M")}'