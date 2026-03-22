from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.movies.models import Movie
from apps.movies.serializers import MovieDetailSerializer, MovieListSerializer

CACHE_TTL_MOVIES = 60 * 5  # 5 minutes


@method_decorator(cache_page(CACHE_TTL_MOVIES), name="dispatch")
class MovieListView(ListAPIView):
    """List all active movies. Cached for 5 minutes."""

    queryset = Movie.objects.filter(is_active=True)
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]
    search_fields = ["title", "genre", "director"]
    ordering_fields = ["title", "release_date", "duration_minutes"]
    filterset_fields = ["genre"]


@method_decorator(cache_page(CACHE_TTL_MOVIES), name="dispatch")
class MovieDetailView(RetrieveAPIView):
    """Retrieve a single movie. Cached for 5 minutes."""

    queryset = Movie.objects.filter(is_active=True)
    serializer_class = MovieDetailSerializer
    permission_classes = [AllowAny]
