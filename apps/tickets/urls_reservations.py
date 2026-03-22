from django.urls import path

from apps.tickets.views import ReservationCreateView, ReservationDeleteView

urlpatterns = [
    path("", ReservationCreateView.as_view(), name="reservation-create"),
    path(
        "<uuid:pk>/",
        ReservationDeleteView.as_view(),
        name="reservation-delete",
    ),
]
