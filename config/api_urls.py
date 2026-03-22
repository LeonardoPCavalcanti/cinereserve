from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("movies/", include("apps.movies.urls")),
    path("sessions/", include("apps.sessions.urls")),
    path("reservations/", include("apps.tickets.urls_reservations")),
    path("checkout/", include("apps.tickets.urls_checkout")),
    path("tickets/", include("apps.tickets.urls_tickets")),
]
