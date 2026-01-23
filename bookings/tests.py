from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from bookings.models import Booking, Room

User = get_user_model()


class BookingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            password="S3curePassword!2026",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="S3curePassword!2026",
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="S3curePassword!2026",
            is_staff=True,
        )
        self.room = Room.objects.create(
            name="Meeting room",
            capacity=6,
            description="Комната для встреч",
        )

    def booking_payload(self, start_delta=1, duration_hours=1):
        start_time = timezone.now() + timedelta(days=start_delta)
        end_time = start_time + timedelta(hours=duration_hours)
        return {
            "room": self.room.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

    def test_rooms_are_publicly_readable(self):
        response = self.client.get(reverse("room-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], "Meeting room")

    def test_only_admin_can_create_room(self):
        response = self.client.post(
            reverse("room-list"),
            {"name": "Private room", "capacity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("room-list"),
            {"name": "Private room", "capacity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Room.objects.filter(name="Private room").exists())

    def test_booking_requires_authentication(self):
        response = self.client.post(
            reverse("booking-list"),
            self.booking_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_booking_for_self(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("booking-list"),
            self.booking_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.Status.ACTIVE)

    def test_user_cannot_create_overlapping_booking(self):
        payload = self.booking_payload()
        self.client.force_authenticate(user=self.user)
        first_response = self.client.post(reverse("booking-list"), payload, format="json")

        second_response = self.client.post(reverse("booking-list"), payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_user_sees_only_own_bookings(self):
        own_booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1),
        )
        Booking.objects.create(
            user=self.other_user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=3),
            end_time=timezone.now() + timedelta(days=3, hours=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], own_booking.id)

    def test_user_cannot_retrieve_other_booking(self):
        booking = Booking.objects.create(
            user=self.other_user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=4),
            end_time=timezone.now() + timedelta(days=4, hours=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("booking-detail", args=[booking.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_cancel_own_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=5),
            end_time=timezone.now() + timedelta(days=5, hours=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse("booking-cancel", args=[booking.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELED)

    def test_admin_sees_all_bookings(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=6),
            end_time=timezone.now() + timedelta(days=6, hours=1),
        )
        Booking.objects.create(
            user=self.other_user,
            room=self.room,
            start_time=timezone.now() + timedelta(days=7),
            end_time=timezone.now() + timedelta(days=7, hours=1),
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
