from django_filters import rest_framework as filters

from bookings.models import Booking, Room


class RoomFilter(filters.FilterSet):
    min_capacity = filters.NumberFilter(field_name="capacity", lookup_expr="gte")
    max_capacity = filters.NumberFilter(field_name="capacity", lookup_expr="lte")

    class Meta:
        model = Room
        fields = ("min_capacity", "max_capacity")


class BookingFilter(filters.FilterSet):
    room = filters.NumberFilter(field_name="room_id")
    start_after = filters.IsoDateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_before = filters.IsoDateTimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:
        model = Booking
        fields = ("room", "status", "start_after", "end_before")
