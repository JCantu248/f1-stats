# Create your tests here.
from datetime import date

from django.test import TestCase
from django.urls import reverse

from racing.models import Circuit, Driver, Race, Season


class RaceApiTests(TestCase):
    def setUp(self):
        self.season = Season.objects.create(year=2026)

        self.circuit = Circuit.objects.create(
            name="Albert Park Grand Prix Circuit",
            city="Melbourne",
            country="Australia",
        )

        self.race = Race.objects.create(
            season=self.season,
            round_number=1,
            name="Australian Grand Prix",
            circuit=self.circuit,
            race_date=date(2026, 3, 8),
        )

    def test_race_list_returns_race(self):
        response = self.client.get(
            reverse("racing:race-list")
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["name"],
            "Australian Grand Prix",
        )
        self.assertEqual(
            data["results"][0]["season"],
            2026,
        )
        self.assertEqual(
            data["results"][0]["circuit"]["country"],
            "Australia",
        )

    def test_race_detail_returns_404_for_unknown_race(self):
        response = self.client.get(
            reverse(
                "racing:race-detail",
                kwargs={"race_id": 9999},
            )
        )

        self.assertEqual(response.status_code, 404)


class DriverApiTests(TestCase):
    def setUp(self):
        self.driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            nationality="Dutch",
            permanent_number=3,
        )

    def test_driver_list_returns_driver(self):
        response = self.client.get(
            reverse("racing:driver-list")
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["name"],
            "Max Verstappen",
        )
        self.assertEqual(
            data["results"][0]["number"],
            3,
        )
        self.assertEqual(
            data["results"][0]["nationality"],
            "Dutch",
        )