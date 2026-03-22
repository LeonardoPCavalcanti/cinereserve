from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:pk>/", views.CinemaSessionDetailView.as_view(), name="session-detail"),
    path(
        "<uuid:pk>/seats/", views.SessionSeatMapView.as_view(), name="session-seats"
    ),
]
