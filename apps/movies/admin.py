from django.contrib import admin

from apps.movies.models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "genre",
        "director",
        "duration_minutes",
        "release_date",
        "is_active",
    ]
    search_fields = ["title", "genre", "director"]
    list_filter = ["genre", "is_active", "release_date"]
