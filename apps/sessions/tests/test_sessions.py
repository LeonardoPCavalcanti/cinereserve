from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.movies.models import Movie
from apps.seats.models import Room, Seat, SeatStatus
from apps.sessions.models import CinemaSession

User = get_user_model()


class CinemaSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="A test movie description.",
            duration_minutes=120,
            genre="Action",
            director="Test Director",
            release_date="2026-01-01",
        )

        self.room = Room.objects.create(
            name="Room 1",
            total_rows=2,
            seats_per_row=3,
        )

        # Create seats for the room
        self.seats = []
        for row_letter in ["A", "B"]:
            for number in range(1, 4):
                seat = Seat.objects.create(
                    room=self.room,
                    row=row_letter,
                    number=number,
                )
                self.seats.append(seat)

        self.session = CinemaSession.objects.create(
            movie=self.movie,
            room=self.room,
            start_time=timezone.now() + timedelta(days=1),
            language="Portugues",
            format="2D",
        )

        # Create SeatStatus records for the session
        self.seat_statuses = []
        for seat in self.seats:
            ss = SeatStatus.objects.create(
                session=self.session,
                seat=seat,
                status="available",
            )
            self.seat_statuses.append(ss)

    def test_end_time_computed_on_save(self):
        """end_time should be start_time + movie.duration_minutes."""
        expected_end = self.session.start_time + timedelta(minutes=self.movie.duration_minutes)
        self.assertEqual(self.session.end_time, expected_end)

    def test_list_sessions_for_movie(self):
        """GET /api/v1/movies/{movie_id}/sessions/ returns sessions."""
        url = reverse("movie-sessions-list", kwargs={"movie_id": self.movie.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["movie"]["title"], "Test Movie")

    def test_session_detail(self):
        """GET /api/v1/sessions/{id}/ returns session detail."""
        url = reverse("session-detail", kwargs={"pk": self.session.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["movie"]["title"], "Test Movie")
        self.assertEqual(response.data["room"]["name"], "Room 1")
        self.assertEqual(response.data["language"], "Portugues")
        self.assertEqual(response.data["format"], "2D")

    def test_seat_map(self):
        """GET /api/v1/sessions/{id}/seats/ returns correct seat statuses."""
        url = reverse("session-seats", kwargs={"pk": self.session.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["session_id"]), str(self.session.id))
        self.assertEqual(response.data["room"], "Room 1")
        self.assertEqual(len(response.data["seats"]), 6)

        # All seats should be available
        for seat_data in response.data["seats"]:
            self.assertEqual(seat_data["status"], "available")

    def test_seat_map_auto_creates_statuses(self):
        """When no SeatStatus exists, they are auto-created."""
        # Create a new session with no SeatStatus records
        new_session = CinemaSession.objects.create(
            movie=self.movie,
            room=self.room,
            start_time=timezone.now() + timedelta(days=2),
            language="Ingles Legendado",
            format="3D",
        )

        # Verify no SeatStatus exists for new session
        self.assertEqual(SeatStatus.objects.filter(session=new_session).count(), 0)

        url = reverse("session-seats", kwargs={"pk": new_session.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should have auto-created statuses for all 6 seats
        self.assertEqual(len(response.data["seats"]), 6)
        self.assertEqual(SeatStatus.objects.filter(session=new_session).count(), 6)

        for seat_data in response.data["seats"]:
            self.assertEqual(seat_data["status"], "available")
