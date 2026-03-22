from django.urls import include, path

from apps.movies.views import MovieDetailView, MovieListView

urlpatterns = [
    path("", MovieListView.as_view(), name="movie-list"),
    path("<uuid:pk>/", MovieDetailView.as_view(), name="movie-detail"),
    path("<uuid:movie_id>/sessions/", include("apps.sessions.urls_movie_sessions")),
]
