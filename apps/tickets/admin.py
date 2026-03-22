from django.contrib import admin

from apps.tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_code",
        "user",
        "session",
        "seat",
        "status",
        "purchased_at",
    ]
    list_filter = ["status", "purchased_at"]
    search_fields = ["ticket_code", "user__email"]
    readonly_fields = ["id", "ticket_code", "purchased_at", "created_at"]
    ordering = ["-purchased_at"]
