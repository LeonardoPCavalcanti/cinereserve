from django.contrib import admin

from .models import Room, Seat, SeatStatus


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "total_rows", "seats_per_row", "created_at"]


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["room", "row", "number", "seat_label"]
    list_filter = ["room"]


@admin.register(SeatStatus)
class SeatStatusAdmin(admin.ModelAdmin):
    list_display = ["seat", "session", "status", "locked_by", "locked_until"]
    list_filter = ["status"]
