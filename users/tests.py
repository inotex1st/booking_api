from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "ivan",
                "email": "ivan@example.com",
                "first_name": "Иван",
                "last_name": "Петров",
                "password": "S3curePassword!2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="ivan").exists())
        self.assertNotIn("password", response.data)

    def test_token_obtain_pair(self):
        User.objects.create_user(username="olga", password="S3curePassword!2026")

        response = self.client.post(
            reverse("token-obtain-pair"),
            {"username": "olga", "password": "S3curePassword!2026"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_returns_authenticated_user(self):
        user = User.objects.create_user(
            username="maria",
            email="maria@example.com",
            password="S3curePassword!2026",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "maria")
        self.assertEqual(response.data["email"], "maria@example.com")
