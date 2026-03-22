from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.seats.models import Seat, SeatStatus
from apps.sessions.models import CinemaSession
from apps.tickets.models import Ticket
from apps.tickets.serializers import (
    CheckoutResponseSerializer,
    CheckoutSerializer,
    ReservationCreateSerializer,
    ReservationResponseSerializer,
    TicketSerializer,
)
from core.redis_lock import acquire_seat_lock, release_seat_lock


class ReservationCreateView(generics.CreateAPIView):
    """Reserve a seat for a cinema session (10-minute lock)."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        seat_id = serializer.validated_data["seat_id"]
        user = request.user

        # Validate session and seat exist
        try:
            cinema_session = CinemaSession.objects.get(id=session_id)
        except CinemaSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            seat = Seat.objects.get(id=seat_id)
        except Seat.DoesNotExist:
            return Response(
                {"detail": "Seat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check SeatStatus
        try:
            seat_status = SeatStatus.objects.get(session=cinema_session, seat=seat)
        except SeatStatus.DoesNotExist:
            return Response(
                {"detail": "Seat status not found for this session."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if seat_status.status != "available":
            return Response(
                {"detail": "Seat is not available."},
                status=status.HTTP_409_CONFLICT,
            )

        # Acquire Redis lock
        lock_acquired = acquire_seat_lock(str(session_id), str(seat_id), str(user.id))
        if not lock_acquired:
            return Response(
                {"detail": "Seat is currently being reserved by another user."},
                status=status.HTTP_409_CONFLICT,
            )

        # Update SeatStatus
        locked_until = timezone.now() + timedelta(minutes=10)
        seat_status.status = "reserved"
        seat_status.locked_by = user
        seat_status.locked_until = locked_until
        seat_status.save()

        response_data = {
            "reservation_id": seat_status.id,
            "session_id": session_id,
            "seat_id": seat_id,
            "seat_label": seat.seat_label,
            "locked_until": locked_until,
            "status": "reserved",
        }
        response_serializer = ReservationResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReservationDeleteView(generics.DestroyAPIView):
    """Cancel a reservation and release the seat lock."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SeatStatus.objects.filter(locked_by=self.request.user, status="reserved")

    def perform_destroy(self, instance):
        # Release Redis lock
        release_seat_lock(
            str(instance.session_id),
            str(instance.seat_id),
            str(self.request.user.id),
        )

        # Reset SeatStatus
        instance.status = "available"
        instance.locked_by = None
        instance.locked_until = None
        instance.save()


class CheckoutView(generics.CreateAPIView):
    """Complete the purchase of a reserved seat."""

    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_id = serializer.validated_data["reservation_id"]

        # Validate reservation
        try:
            seat_status = SeatStatus.objects.select_related(
                "session", "session__movie", "session__room", "seat"
            ).get(id=reservation_id)
        except SeatStatus.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if seat_status.status != "reserved":
            return Response(
                {"detail": "This seat is not currently reserved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if seat_status.locked_by != request.user:
            return Response(
                {"detail": "This reservation does not belong to you."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if seat_status.locked_until and seat_status.locked_until < timezone.now():
            # Reservation expired — release it
            seat_status.status = "available"
            seat_status.locked_by = None
            seat_status.locked_until = None
            seat_status.save()
            return Response(
                {"detail": "Reservation has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create ticket
        ticket = Ticket.objects.create(
            user=request.user,
            session=seat_status.session,
            seat=seat_status.seat,
        )

        # Update SeatStatus to purchased
        seat_status.status = "purchased"
        seat_status.locked_by = None
        seat_status.locked_until = None
        seat_status.save()

        # Release Redis lock
        release_seat_lock(
            str(seat_status.session_id),
            str(seat_status.seat_id),
            str(request.user.id),
        )

        response_serializer = CheckoutResponseSerializer(ticket)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TicketListView(generics.ListAPIView):
    """List all tickets for the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related(
            "session", "session__movie", "session__room", "seat"
        )


class TicketActiveListView(generics.ListAPIView):
    """List active tickets for upcoming sessions."""

    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(
            user=self.request.user,
            status="active",
            session__start_time__gt=timezone.now(),
        ).select_related("session", "session__movie", "session__room", "seat")


class TicketHistoryListView(generics.ListAPIView):
    """List all tickets (history) for the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related(
            "session", "session__movie", "session__room", "seat"
        )


class TicketDetailView(generics.RetrieveAPIView):
    """Retrieve a single ticket detail."""

    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related(
            "session", "session__movie", "session__room", "seat"
        )
