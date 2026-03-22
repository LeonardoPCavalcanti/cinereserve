import uuid
from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.movies.models import Movie


class MovieAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.active_movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller about dream infiltration.",
            duration_minutes=148,
            genre="Sci-Fi",
            director="Christopher Nolan",
            cast="Leonardo DiCaprio, Joseph Gordon-Levitt",
            release_date=date(2010, 7, 16),
            is_active=True,
        )

        self.inactive_movie = Movie.objects.create(
            title="Old Movie",
            description="An inactive movie that should not appear in listings.",
            duration_minutes=90,
            genre="Drama",
            director="Some Director",
            cast="Actor A, Actor B",
            release_date=date(2000, 1, 1),
            is_active=False,
        )

    def test_list_movies(self):
        """GET /api/v1/movies/ returns only active movies."""
        url = reverse("movie-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)
        if isinstance(results, list):
            titles = [movie["title"] for movie in results]
        else:
            titles = [movie["title"] for movie in results]

        self.assertIn("Inception", titles)
        self.assertNotIn("Old Movie", titles)

    def test_list_movies_pagination(self):
        """Verify pagination structure in the response."""
        url = reverse("movie-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict):
            self.assertIn("results", response.data)
            self.assertIn("count", response.data)

    def test_movie_detail(self):
        """GET /api/v1/movies/{id}/ returns the correct movie."""
        url = reverse("movie-detail", kwargs={"pk": self.active_movie.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Inception")
        self.assertEqual(response.data["director"], "Christopher Nolan")
        self.assertIn("cast", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_movie_detail_not_found(self):
        """GET /api/v1/movies/{invalid_id}/ returns 404."""
        fake_uuid = uuid.uuid4()
        url = reverse("movie-detail", kwargs={"pk": fake_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
