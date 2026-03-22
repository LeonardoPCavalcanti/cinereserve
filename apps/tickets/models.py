import uuid

from django.conf import settings
from django.db import models


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("used", "Used"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_code = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    session = models.ForeignKey(
        "cinema_sessions.CinemaSession",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    seat = models.ForeignKey(
        "seats.Seat",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active"
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("session", "seat")]
        ordering = ["-purchased_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_code} - {self.user}"
