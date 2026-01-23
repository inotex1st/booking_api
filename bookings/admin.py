from django.contrib import admin

from bookings.models import Booking, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "start_time", "end_time", "status", "created_at")
    list_filter = ("status", "room", "start_time")
    search_fields = ("room__name", "user__username", "user__email")
    date_hierarchy = "start_time"
    readonly_fields = ("created_at", "updated_at")
