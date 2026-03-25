import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from db.models import Booking, Table


class TableTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.table1 = Table.objects.create(name="Table 1")
        self.table2 = Table.objects.create(name="Table 2")

    def test_list_success(self):
        response = self.client.get(reverse("api:table-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_available_success(self):
        future = datetime.datetime.now() + datetime.timedelta(days=1)

        Booking.objects.create(
            table=self.table1,
            date=future,
            client_name="John",
            client_phone="123",
        )
        response = self.client.get(
            reverse("api:table-available"),
            {"date": future.strftime("%d.%m.%YT%H:%M")},
        )
        self.assertEqual(response.status_code, 200)
        ids = [t["id"] for t in response.data]
        self.assertNotIn(self.table1.id, ids)
        self.assertIn(self.table2.id, ids)

    def test_missing_date_return_400(self):
        response = self.client.get(reverse("api:table-available"))
        self.assertEqual(response.status_code, 400)

    def test_available_past_date_return_400(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        response = self.client.get(
            reverse("api:table-available"),
            {"date": past.strftime("%d.%m.%YT%H:%M")},
        )
        self.assertEqual(response.status_code, 400)


class BookingCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.table = Table.objects.create(name="Table 1")

    def _booking_data(self, **kwargs):
        future = (
            datetime.datetime.now() + datetime.timedelta(days=1)
        ).strftime("%d.%m.%YT%H:%M")

        data = {
            "table": self.table.id,
            "date": future,
            "client_name": "Bob",
            "client_phone": "+380991234567",
        }
        data.update(kwargs)

        return data

    def test_create_success(self):
        response = self.client.post(reverse("api:booking-list"), self._booking_data())
        self.assertEqual(response.status_code, 201)
        for field in ("id", "table", "date", "client_name", "client_phone"):
            self.assertIn(field, response.data)

    def test_create_past_date_returns_400(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        response = self.client.post(
            reverse("api:booking-list"),
            self._booking_data(date=past.strftime("%d.%m.%YT%H:%M")),
        )
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_in_two_hours_returns_400(self):
        self.client.post(reverse("api:booking-list"), self._booking_data())
        response = self.client.post(reverse("api:booking-list"), self._booking_data())
        self.assertEqual(response.status_code, 400)

    def test_create_short_name_returns_400(self):
        response = self.client.post(reverse("api:booking-list"), self._booking_data(client_name="B"))
        self.assertEqual(response.status_code, 400)

    def test_create_invalid_phone_returns_400(self):
        response = self.client.post(reverse("api:booking-list"), self._booking_data(client_phone="notaphone"))
        self.assertEqual(response.status_code, 400)
