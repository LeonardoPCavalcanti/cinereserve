from django.urls import path

from apps.tickets.views import (
    TicketActiveListView,
    TicketDetailView,
    TicketHistoryListView,
    TicketListView,
)

urlpatterns = [
    path("", TicketListView.as_view(), name="ticket-list"),
    path("active/", TicketActiveListView.as_view(), name="ticket-active-list"),
    path("history/", TicketHistoryListView.as_view(), name="ticket-history-list"),
    path("<uuid:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
]
