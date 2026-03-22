import uuid
from datetime import timedelta

from django.db import models


class CinemaSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(
        "movies.Movie", on_delete=models.CASCADE, related_name="sessions"
    )
    room = models.ForeignKey(
        "seats.Room", on_delete=models.CASCADE, related_name="sessions"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True)
    language = models.CharField(max_length=50)
    format = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_time}"

    def save(self, *args, **kwargs):
        if self.start_time and self.movie_id:
            self.end_time = self.start_time + timedelta(
                minutes=self.movie.duration_minutes
            )
        super().save(*args, **kwargs)
