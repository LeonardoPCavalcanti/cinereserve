import uuid

from django.conf import settings
from django.db import models


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    total_rows = models.PositiveIntegerField()
    seats_per_row = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()
    seat_label = models.CharField(max_length=5)

    class Meta:
        ordering = ["row", "number"]
        unique_together = [("room", "row", "number")]

    def save(self, *args, **kwargs):
        self.seat_label = f"{self.row}{self.number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room.name} - {self.seat_label}"


class SeatStatus(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("purchased", "Purchased"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        "cinema_sessions.CinemaSession",
        on_delete=models.CASCADE,
        related_name="seat_statuses",
    )
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="statuses")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("session", "seat")]

    def __str__(self):
        return f"{self.seat} - {self.status}"
