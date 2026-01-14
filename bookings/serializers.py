from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from bookings.models import Booking, Room

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "capacity", "description", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class BookingSerializer(serializers.ModelSerializer):
    room_detail = RoomSerializer(source="room", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Booking
        fields = (
            "id",
            "room",
            "room_detail",
            "user",
            "user_username",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        instance = self.instance

        if request and not request.user.is_staff:
            attrs["user"] = request.user
            if instance is None:
                attrs["status"] = Booking.Status.ACTIVE
        elif request and "user" not in attrs and instance is None:
            attrs["user"] = request.user

        room = attrs.get("room", getattr(instance, "room", None))
        user = attrs.get("user", getattr(instance, "user", None))
        start_time = attrs.get("start_time", getattr(instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(instance, "end_time", None))
        status = attrs.get("status", getattr(instance, "status", Booking.Status.ACTIVE))

        if room and user and start_time and end_time:
            candidate = Booking(
                room=room,
                user=user,
                start_time=start_time,
                end_time=end_time,
                status=status,
            )
            if instance:
                candidate.pk = instance.pk

            try:
                candidate.clean()
            except DjangoValidationError as error:
                detail = getattr(error, "message_dict", error.messages)
                raise serializers.ValidationError(detail) from error

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            # лочим комнату, чтобы два запроса не заняли одно и то же время
            Room.objects.select_for_update().get(pk=validated_data["room"].pk)
            booking = Booking(**validated_data)
            booking.save()
            return booking

    def update(self, instance, validated_data):
        with transaction.atomic():
            room = validated_data.get("room", instance.room)
            # при переносе брони проверяем новую комнату так же строго
            Room.objects.select_for_update().get(pk=room.pk)

            for field, value in validated_data.items():
                setattr(instance, field, value)
            instance.save()
            return instance
