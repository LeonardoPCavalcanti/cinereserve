import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.movies.models import Movie
from apps.seats.models import Room, Seat, SeatStatus
from apps.sessions.models import CinemaSession
from apps.tickets.models import Ticket
from apps.users.models import User


class TicketFlowTests(TestCase):
    """End-to-end tests for reservation, checkout, and ticket endpoints."""

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123",
        )

        # JWT tokens
        self.token1 = str(RefreshToken.for_user(self.user1).access_token)
        self.token2 = str(RefreshToken.for_user(self.user2).access_token)

        # Create movie
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="A test movie",
            duration_minutes=120,
            genre="Action",
            director="Test Director",
            release_date="2026-01-01",
        )

        # Create room and seats
        self.room = Room.objects.create(
            name="Room 1",
            total_rows=5,
            seats_per_row=10,
        )
        self.seat1 = Seat.objects.create(room=self.room, row="A", number=1)
        self.seat2 = Seat.objects.create(room=self.room, row="A", number=2)

        # Create session
        self.session = CinemaSession.objects.create(
            movie=self.movie,
            room=self.room,
            start_time=timezone.now() + timedelta(days=1),
            language="English",
            format="2D",
        )

        # Create seat statuses
        self.seat_status1 = SeatStatus.objects.create(
            session=self.session,
            seat=self.seat1,
            status="available",
        )
        self.seat_status2 = SeatStatus.objects.create(
            session=self.session,
            seat=self.seat2,
            status="available",
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ── Reservation Tests ─────────────────────────────────────────

    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_reserve_seat_success(self, mock_lock):
        self._auth(self.token1)
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "reserved")
        self.assertEqual(response.data["seat_label"], self.seat1.seat_label)

        # Verify SeatStatus was updated
        self.seat_status1.refresh_from_db()
        self.assertEqual(self.seat_status1.status, "reserved")
        self.assertEqual(self.seat_status1.locked_by, self.user1)
        self.assertIsNotNone(self.seat_status1.locked_until)

    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_reserve_already_reserved(self, mock_lock):
        self._auth(self.token1)
        # First reservation
        self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        # Second reservation for same seat
        self._auth(self.token2)
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_cancel_reservation(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Create reservation
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        reservation_id = response.data["reservation_id"]

        # Cancel it
        response = self.client.delete(f"/api/v1/reservations/{reservation_id}/")
        self.assertEqual(response.status_code, 204)

        # Verify seat is available again
        self.seat_status1.refresh_from_db()
        self.assertEqual(self.seat_status1.status, "available")
        self.assertIsNone(self.seat_status1.locked_by)

    # ── Checkout Tests ────────────────────────────────────────────

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_checkout_success(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Reserve first
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        reservation_id = response.data["reservation_id"]

        # Checkout
        response = self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(reservation_id)},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("ticket_code", response.data)
        self.assertIn("ticket_id", response.data)

        # Verify ticket was created
        self.assertTrue(Ticket.objects.filter(user=self.user1).exists())

        # Verify SeatStatus is purchased
        self.seat_status1.refresh_from_db()
        self.assertEqual(self.seat_status1.status, "purchased")

    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_checkout_expired(self, mock_acquire):
        self._auth(self.token1)
        # Reserve
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        reservation_id = response.data["reservation_id"]

        # Manually expire the reservation
        self.seat_status1.refresh_from_db()
        self.seat_status1.locked_until = timezone.now() - timedelta(minutes=1)
        self.seat_status1.save()

        # Try checkout
        response = self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(reservation_id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.data["detail"].lower())

    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_checkout_wrong_user(self, mock_acquire):
        self._auth(self.token1)
        # User1 reserves
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        reservation_id = response.data["reservation_id"]

        # User2 tries to checkout
        self._auth(self.token2)
        response = self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(reservation_id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    # ── Ticket Tests ──────────────────────────────────────────────

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_my_tickets(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Reserve and checkout
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(response.data["reservation_id"])},
            format="json",
        )

        # Get tickets
        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_active_tickets(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Reserve and checkout
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(response.data["reservation_id"])},
            format="json",
        )

        # Get active tickets (session is in the future)
        response = self.client.get("/api/v1/tickets/active/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_ticket_history(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Reserve and checkout
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(response.data["reservation_id"])},
            format="json",
        )

        # Get history
        response = self.client.get("/api/v1/tickets/history/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    @patch("apps.tickets.views.release_seat_lock", return_value=True)
    @patch("apps.tickets.views.acquire_seat_lock", return_value=True)
    def test_ticket_detail(self, mock_acquire, mock_release):
        self._auth(self.token1)
        # Reserve and checkout
        response = self.client.post(
            "/api/v1/reservations/",
            {"session_id": str(self.session.id), "seat_id": str(self.seat1.id)},
            format="json",
        )
        checkout_response = self.client.post(
            "/api/v1/checkout/",
            {"reservation_id": str(response.data["reservation_id"])},
            format="json",
        )
        ticket_id = checkout_response.data["ticket_id"]

        # Get detail
        response = self.client.get(f"/api/v1/tickets/{ticket_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(ticket_id))
        self.assertIn("ticket_code", response.data)
