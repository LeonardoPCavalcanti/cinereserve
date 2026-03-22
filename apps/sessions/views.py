from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.seats.models import SeatStatus

from .models import CinemaSession
from .serializers import (
    CinemaSessionDetailSerializer,
    CinemaSessionListSerializer,
    SessionSeatMapSerializer,
)

CACHE_TTL_SESSIONS = 60 * 2  # 2 minutes


@method_decorator(cache_page(CACHE_TTL_SESSIONS), name="dispatch")
class MovieSessionsListView(generics.ListAPIView):
    """List sessions for a specific movie. Cached for 2 minutes."""

    serializer_class = CinemaSessionListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        return CinemaSession.objects.filter(movie_id=movie_id, is_active=True).select_related("movie", "room")


@method_decorator(cache_page(CACHE_TTL_SESSIONS), name="dispatch")
class CinemaSessionDetailView(generics.RetrieveAPIView):
    """Detail of a cinema session. Cached for 2 minutes."""

    queryset = CinemaSession.objects.select_related("movie", "room")
    serializer_class = CinemaSessionDetailSerializer
    permission_classes = [AllowAny]


class SessionSeatMapView(generics.GenericAPIView):
    """GET returns the seat map for a session."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            session = CinemaSession.objects.select_related("room").get(pk=pk)
        except CinemaSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        # Auto-create SeatStatus records if none exist for this session
        existing = SeatStatus.objects.filter(session=session).exists()
        if not existing:
            seats = session.room.seats.all()
            seat_statuses = [
                SeatStatus(session=session, seat=seat, status="available")
                for seat in seats
            ]
            SeatStatus.objects.bulk_create(seat_statuses)

        seat_statuses = (
            SeatStatus.objects.filter(session=session)
            .select_related("seat")
            .order_by("seat__row", "seat__number")
        )

        serializer = SessionSeatMapSerializer(
            {
                "session_id": session.id,
                "room": session.room.name,
                "seats": seat_statuses,
            }
        )
        return Response(serializer.data)
