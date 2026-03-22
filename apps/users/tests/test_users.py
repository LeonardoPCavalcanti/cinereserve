from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class UserAuthTests(TestCase):
    """Tests for user registration, login, token refresh, and logout."""

    def setUp(self) -> None:
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.token_refresh_url = reverse("users:token-refresh")
        self.logout_url = reverse("users:logout")

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
            "password_confirm": "securepassword123",
        }

    def _create_user(self) -> "User":
        """Helper to create a user directly in the database."""
        return User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

    # ── Registration ──────────────────────────────────────────────────

    def test_register_success(self) -> None:
        response = self.client.post(self.register_url, self.user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIn("access", data["tokens"])
        self.assertIn("refresh", data["tokens"])
        self.assertEqual(data["user"]["email"], self.user_data["email"])
        self.assertEqual(User.objects.count(), 1)

    def test_register_duplicate_email(self) -> None:
        self._create_user()
        response = self.client.post(self.register_url, self.user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self) -> None:
        payload = {**self.user_data, "password_confirm": "differentpassword"}
        response = self.client.post(self.register_url, payload, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Login ─────────────────────────────────────────────────────────

    def test_login_success(self) -> None:
        self._create_user()
        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIn("access", data["tokens"])
        self.assertIn("refresh", data["tokens"])
        self.assertEqual(data["user"]["email"], self.user_data["email"])

    def test_login_wrong_credentials(self) -> None:
        self._create_user()
        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": "wrongpassword",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Token refresh ─────────────────────────────────────────────────

    def test_token_refresh(self) -> None:
        self._create_user()
        login_response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            content_type="application/json",
        )
        refresh_token = login_response.json()["tokens"]["refresh"]

        response = self.client.post(
            self.token_refresh_url,
            {"refresh": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

    # ── Logout ────────────────────────────────────────────────────────

    def test_logout(self) -> None:
        self._create_user()
        login_response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            content_type="application/json",
        )
        tokens = login_response.json()["tokens"]

        response = self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the refresh token is now blacklisted
        refresh_response = self.client.post(
            self.token_refresh_url,
            {"refresh": tokens["refresh"]},
            content_type="application/json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
