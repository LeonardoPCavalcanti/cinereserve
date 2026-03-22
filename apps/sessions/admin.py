from django.contrib import admin

from .models import CinemaSession


@admin.register(CinemaSession)
class CinemaSessionAdmin(admin.ModelAdmin):
    list_display = [
        "movie",
        "room",
        "start_time",
        "end_time",
        "language",
        "format",
        "is_active",
    ]
    list_filter = ["is_active", "language", "format", "room"]
    search_fields = ["movie__title", "room__name"]
    ordering = ["-start_time"]
