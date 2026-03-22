from django.urls import path

from . import views

urlpatterns = [
    path("", views.MovieSessionsListView.as_view(), name="movie-sessions-list"),
]
