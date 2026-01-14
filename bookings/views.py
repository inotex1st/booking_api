from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.filters import BookingFilter, RoomFilter
from bookings.models import Booking, Room
from bookings.permissions import IsAdminOrReadOnly
from bookings.serializers import BookingSerializer, RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = RoomFilter
    search_fields = ("name", "description")
    ordering_fields = ("name", "capacity", "created_at")
    ordering = ("name",)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    filterset_class = BookingFilter
    search_fields = ("room__name", "user__username")
    ordering_fields = ("start_time", "end_time", "created_at", "status")
    ordering = ("-created_at",)

    def get_queryset(self):
        # пользователь видит свое, админ видит весь календарь
        queryset = Booking.objects.select_related("room", "user")
        if not self.request.user.is_authenticated:
            return queryset.none()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            permission_classes = (permissions.IsAdminUser,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=("post",))
    def cancel(self, request, pk=None):
        # отмену оставляем в истории, поэтому запись не удаляем
        booking = self.get_object()
        if booking.status == Booking.Status.CANCELED:
            return Response(
                {"detail": "Бронирование уже отменено."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.cancel()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
